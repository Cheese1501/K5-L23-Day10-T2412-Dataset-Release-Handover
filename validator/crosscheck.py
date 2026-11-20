#!/usr/bin/env python3
"""Detection <-> panoptic cross-check.

Only reads the supplied delivery directory. Uses Python standard library
and scripts/pngutil.py. Findings are candidates, not confirmed errors.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import pngutil  # noqa: E402


DEFAULTS = {
    "min_segment_pixels": 128,
    "min_spatial_iou": 0.05,
    "min_segment_coverage": 0.15,
    "min_box_coverage_for_merge": 0.15,
    "drift_inside_ratio": 0.75,
}


def load_classes(path: Path) -> dict[int, str]:
    result = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.strip().split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"classes.txt:{line_no}: invalid row")
        class_id = int(parts[0])
        if class_id in result:
            raise ValueError(f"classes.txt:{line_no}: duplicate class id {class_id}")
        result[class_id] = parts[1].strip()
    return result


def load_boxes(path: Path, classes: dict[int, str], width: int, height: int):
    """Read YOLO rows and return pixel xyxy boxes."""
    boxes = []
    if not path.is_file():
        return boxes

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            continue
        try:
            class_id = int(fields[0])
            xc, yc, bw, bh = map(float, fields[1:])
        except ValueError:
            continue

        if class_id not in classes or bw <= 0 or bh <= 0:
            continue

        x1 = (xc - bw / 2) * width
        y1 = (yc - bh / 2) * height
        x2 = (xc + bw / 2) * width
        y2 = (yc + bh / 2) * height

        # Clip only for geometric comparison; preserve original coordinates
        # in the delivery and do not silently rewrite labels.
        x1c, y1c = max(0.0, x1), max(0.0, y1)
        x2c, y2c = min(float(width), x2), min(float(height), y2)
        if x2c <= x1c or y2c <= y1c:
            continue

        boxes.append({
            "index": len(boxes),
            "class_id": class_id,
            "class_name": classes[class_id],
            "xyxy": (x1c, y1c, x2c, y2c),
            "original_xyxy": (x1, y1, x2, y2),
        })
    return boxes


def box_area(box):
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def intersection_area(a, b):
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def box_iou(a, b):
    inter = intersection_area(a, b)
    union = box_area(a) + box_area(b) - inter
    return inter / union if union > 0 else 0.0


def read_segment_pixels(mask_path: Path):
    """Return mask dimensions and pixel coordinates grouped by segment id."""
    width, height, pixels = pngutil.read_rgb(mask_path)
    found = defaultdict(list)

    for offset in range(0, len(pixels), 3):
        sid = pngutil.segment_id(pixels, offset)
        if sid == 0:
            continue
        pixel_index = offset // 3
        x = pixel_index % width
        y = pixel_index // width
        found[sid].append((x, y))

    return width, height, found


def segment_bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (
        float(min(xs)),
        float(min(ys)),
        float(max(xs) + 1),
        float(max(ys) + 1),
    )


def point_in_box(x, y, box):
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def delivery_path(delivery: Path, relative_path: str) -> Path:
    root = delivery.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError(
            f"delivery path escapes delivery directory: {relative_path}"
        )
    return path


def analyze_image(
    stem: str,
    delivery: Path,
    image_info: dict,
    annotation: dict,
    categories: dict,
    detection_classes: dict,
    thresholds: dict,
):
    width = int(image_info["width"])
    height = int(image_info["height"])

    manifest_path = delivery / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    item = manifest.get("items", {}).get(stem, {})

    label_path = delivery_path(
        delivery, item.get("label", f"labels/{stem}.txt")
    )
    mask_path = delivery_path(
        delivery, item.get("mask", f"masks/{stem}.png")
    )

    boxes = load_boxes(label_path, detection_classes, width, height)
    mask_width, mask_height, pixels_by_segment = read_segment_pixels(mask_path)

    if (mask_width, mask_height) != (width, height):
        raise ValueError(
            f"{stem}: image dimensions {width}x{height} "
            f"do not match mask {mask_width}x{mask_height}"
        )

    segments = []
    for seg in annotation.get("segments_info", []):
        if seg.get("iscrowd", 0):
            continue
        category = categories.get(seg.get("category_id"))
        if not category or not category.get("isthing", 0):
            continue

        sid = int(seg["id"])
        points = pixels_by_segment.get(sid, [])
        if not points:
            continue

        segments.append({
            "id": sid,
            "category_id": seg["category_id"],
            "class_name": category["name"],
            "area": len(points),
            "points": points,
            "bbox": segment_bbox(points),
        })

    candidates = []

    def xyxy_to_xywh(rect):
        x1, y1, x2, y2 = rect
        return [x1, y1, x2 - x1, y2 - y1]

    def add_candidate(types, segment, selected_boxes, reason, evidence):
        candidates.append({
            "image": stem,
            "type": types[0],
            "possible_types": types,
            "reason": reason,
            "detection": [
                {
                    "class": box["class_name"],
                    "bbox": xyxy_to_xywh(box["xyxy"]),
                }
                for box in selected_boxes
            ],
            "panoptic": {
                "id": segment["id"],
                "class": segment["class_name"],
                "bbox": xyxy_to_xywh(segment["bbox"]),
            },
            "evidence": evidence,
        })

    for segment in segments:
        points = segment["points"]
        seg_area = len(points)
        if seg_area < thresholds["min_segment_pixels"]:
            continue

        overlaps = []
        for box in boxes:
            inside = sum(
                1 for x, y in points if point_in_box(x, y, box["xyxy"])
            )
            coverage = inside / seg_area
            iou = box_iou(segment["bbox"], box["xyxy"])
            overlaps.append({
                "box": box,
                "inside_pixels": inside,
                "segment_coverage": coverage,
                "bbox_iou": iou,
            })

        spatial = [
            row for row in overlaps
            if row["bbox_iou"] >= thresholds["min_spatial_iou"]
            or row["segment_coverage"] >= thresholds["min_segment_coverage"]
        ]
        spatial.sort(
            key=lambda row: (
                row["segment_coverage"],
                row["bbox_iou"],
            ),
            reverse=True,
        )

        same_class_multi = [
            row for row in overlaps
            if row["box"]["class_name"] == segment["class_name"]
            and row["segment_coverage"] >= thresholds["min_box_coverage_for_merge"]
        ]
        if len(same_class_multi) >= 2:
            selected = [row["box"] for row in same_class_multi]
            reason = "One panoptic segment has substantial pixels in multiple same-class detection boxes"
            add_candidate(
                ["instance_merge"], segment, selected, reason,
                {
                    "segment_pixels": seg_area,
                    "detection_box_indices": [
                        row["box"]["index"] for row in same_class_multi
                    ],
                    "coverage_by_box": [
                        round(row["segment_coverage"], 4)
                        for row in same_class_multi
                    ],
                    "reason": reason,
                },
            )
            continue

        if not spatial:
            reason = "No detection box has sufficient spatial overlap with this thing segment"
            add_candidate(
                ["missing_box"], segment, [], reason,
                {
                    "segment_pixels": seg_area,
                    "reason": reason,
                },
            )
            continue

        best = spatial[0]
        best_box = best["box"]

        if best_box["class_name"] != segment["class_name"]:
            reason = "Spatially corresponding detection and panoptic labels disagree; human review must decide which is wrong"
            add_candidate(
                ["class_swap", "category_swap"], segment, [best_box], reason,
                {
                    "detection_class": best_box["class_name"],
                    "panoptic_class": segment["class_name"],
                    "bbox_iou": round(best["bbox_iou"], 4),
                    "segment_coverage": round(best["segment_coverage"], 4),
                    "reason": reason,
                },
            )
            continue

        if best["segment_coverage"] < thresholds["drift_inside_ratio"]:
            reason = "A substantial fraction of matched segment pixels lies outside the detection box"
            add_candidate(
                ["bbox_drift"], segment, [best_box], reason,
                {
                    "segment_coverage": round(best["segment_coverage"], 4),
                    "bbox_iou": round(best["bbox_iou"], 4),
                    "reason": reason,
                },
            )

    return candidates


def crosscheck(delivery: Path, thresholds: dict | None = None):
    delivery = Path(delivery)
    thresholds = {**DEFAULTS, **(thresholds or {})}

    required = [
        delivery / "classes.txt",
        delivery / "panoptic.json",
        delivery / "manifest.json",
    ]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"required delivery file missing: {path}")

    detection_classes = load_classes(delivery / "classes.txt")
    panoptic = json.loads((delivery / "panoptic.json").read_text(encoding="utf-8"))
    manifest = json.loads((delivery / "manifest.json").read_text(encoding="utf-8"))

    categories = {row["id"]: row for row in panoptic["categories"]}
    images_by_id = {row["id"]: row for row in panoptic["images"]}
    annotations_by_id = {
        row["image_id"]: row for row in panoptic["annotations"]
    }

    output = []
    for image_id, image_info in images_by_id.items():
        annotation = annotations_by_id.get(image_id)
        if annotation is None:
            continue

        stem = Path(image_info["file_name"]).stem
        if stem not in manifest.get("items", {}):
            continue

        output.extend(
            analyze_image(
                stem,
                delivery,
                image_info,
                annotation,
                categories,
                detection_classes,
                thresholds,
            )
        )

    # Stable ordering makes results reproducible.
    output.sort(
        key=lambda row: (
            row["image"],
            ",".join(row["possible_types"]),
            row["evidence"].get("segment_id", -1),
        )
    )
    return {"candidates": output}


def main():
    parser = argparse.ArgumentParser(description="Detection-panoptic cross-check")
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", type=Path, default=Path("candidates.json"))
    parser.add_argument("--min-segment-pixels", type=int, default=DEFAULTS["min_segment_pixels"])
    parser.add_argument("--min-spatial-iou", type=float, default=DEFAULTS["min_spatial_iou"])
    parser.add_argument("--min-segment-coverage", type=float, default=DEFAULTS["min_segment_coverage"])
    parser.add_argument("--drift-inside-ratio", type=float, default=DEFAULTS["drift_inside_ratio"])
    args = parser.parse_args()

    thresholds = {
        "min_segment_pixels": args.min_segment_pixels,
        "min_spatial_iou": args.min_spatial_iou,
        "min_segment_coverage": args.min_segment_coverage,
        "drift_inside_ratio": args.drift_inside_ratio,
    }
    result = crosscheck(args.delivery, thresholds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Candidates: {len(result['candidates'])}")
    print(f"Output: {args.out}")


if __name__ == "__main__":
    main()
