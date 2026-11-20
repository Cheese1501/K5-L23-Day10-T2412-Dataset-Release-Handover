#!/usr/bin/env python3
"""Validate a lab delivery and optionally shortlist cases for human review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pngutil
from validator.rules_detection import find_duplicate_boxes
from validator.rules_panoptic import find_thing_overlaps


class Delivery:
    def __init__(self, root: Path):
        self.root = root.resolve()

        manifest_doc = self.read_json("manifest.json")
        if not isinstance(manifest_doc, dict) or not isinstance(manifest_doc.get("items"), dict):
            raise ValueError("manifest.json phải có trường items dạng object")
        self.manifest = manifest_doc["items"]

        metadata_doc = self.read_json("metadata.json")
        if not isinstance(metadata_doc, dict) or not isinstance(metadata_doc.get("items"), list):
            raise ValueError("metadata.json phải có trường items dạng array")
        self.metadata = {}
        for index, item in enumerate(metadata_doc["items"]):
            if not isinstance(item, dict) or not isinstance(item.get("image"), str) or not item["image"]:
                raise ValueError(f"metadata.json: items[{index}] thiếu image hợp lệ")
            if item["image"] in self.metadata:
                raise ValueError(f"metadata.json có image trùng: {item['image']}")
            self.metadata[item["image"]] = item

        with self.file("jobs.csv").open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not {"job_id", "guideline"}.issubset(reader.fieldnames):
                raise ValueError("jobs.csv phải có cột job_id và guideline")
            self.jobs = {}
            for index, row in enumerate(reader, 2):
                job_id = row.get("job_id")
                if not job_id:
                    raise ValueError(f"jobs.csv: dòng {index} thiếu job_id")
                if job_id in self.jobs:
                    raise ValueError(f"jobs.csv có job_id trùng: {job_id}")
                self.jobs[job_id] = row

        self.classes = {}
        for line_number, line in enumerate(
            self.file("classes.txt").read_text(encoding="utf-8").splitlines(), 1
        ):
            if not line.strip():
                continue
            fields = line.split(maxsplit=1)
            if len(fields) != 2 or not fields[1].strip():
                raise ValueError(f"classes.txt: dòng {line_number} không đúng định dạng '<id> <name>'")
            try:
                class_id = int(fields[0])
            except ValueError as exc:
                raise ValueError(f"classes.txt: class id không hợp lệ ở dòng {line_number}") from exc
            if class_id in self.classes:
                raise ValueError(f"classes.txt có class id trùng: {class_id}")
            self.classes[class_id] = fields[1].strip()

        if not self.classes:
            raise ValueError("classes.txt không có class nào")
        if not isinstance(self.manifest, dict):
            raise ValueError("manifest.json items không hợp lệ")
        for name, row in self.manifest.items():
            if not isinstance(name, str) or not name or not isinstance(row, dict):
                raise ValueError("manifest.json có tên ảnh hoặc item không hợp lệ")

    def file(self, name: str) -> Path:
        path = (self.root / name).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError(f"Đường dẫn nằm ngoài delivery: {name}")
        return path

    def read_json(self, name: str):
        return json.loads(self.file(name).read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class Rect:
    left: float
    top: float
    right: float
    bottom: float

    @classmethod
    def from_xywh(cls, x, y, w, h):
        return cls(x, y, x + w, y + h)

    @property
    def area(self) -> float:
        return max(0, self.right - self.left) * max(0, self.bottom - self.top)

    def intersection(self, other: Rect) -> float:
        return (max(0, min(self.right, other.right) - max(self.left, other.left))
                * max(0, min(self.bottom, other.bottom) - max(self.top, other.top)))

    def xywh(self) -> list[float]:
        return [round(n, 2) for n in
                (self.left, self.top, self.right - self.left, self.bottom - self.top)]


@dataclass(frozen=True)
class Box:
    name: str
    rect: Rect
    center: tuple[float, float]
    size: tuple[float, float]


@dataclass(frozen=True)
class Segment:
    id: int
    name: str
    rect: Rect
    area: int


def detection(path: Path, classes: dict, width: int, height: int) -> tuple[list[Box], set[str]]:
    boxes = []
    errors = set()

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        fields = line.split()
        try:
            category = float(fields[0])
        except (ValueError, IndexError):
            errors.add("invalid_class")
            continue

        if (not math.isfinite(category)
                or not category.is_integer()
                or int(category) not in classes):
            errors.add("invalid_class")
            continue

        if len(fields) < 5:
            errors.add("bbox_out_of_bounds")
            continue

        try:
            x, y, w, h = map(float, fields[1:5])
        except ValueError:
            errors.add("bbox_out_of_bounds")
            continue

        if not all(map(math.isfinite, (x, y, w, h))):
            errors.add("bbox_out_of_bounds")
            continue

        rect = Rect(
            (x - w / 2) * width,
            (y - h / 2) * height,
            (x + w / 2) * width,
            (y + h / 2) * height,
        )

        epsilon = max(width, height) * 0.000001
        if (min(w, h) <= 0
                or min(rect.left, rect.top) < -epsilon
                or rect.right > width + epsilon
                or rect.bottom > height + epsilon):
            errors.add("bbox_out_of_bounds")
            continue

        boxes.append(Box(
            classes[int(category)],
            rect,
            (x * width, y * height),
            (w * width, h * height),
        ))

    return boxes, errors


def mask_runs(path: Path) -> tuple[Counter, dict]:
    width, _, rgb = pngutil.read_rgb(path)
    counts = Counter()
    runs = defaultdict(list)
    for y, start in enumerate(range(0, len(rgb), width * 3)):
        last = -1
        left = 0
        for x, offset in enumerate(range(start, start + width * 3, 3)):
            sid = rgb[offset] | (rgb[offset + 1] << 8) | (rgb[offset + 2] << 16)
            if sid != last:
                if last > 0:
                    counts[last] += x - left
                    runs[last].append((y, left, x))
                last, left = sid, x
        if last > 0:
            counts[last] += width - left
            runs[last].append((y, left, width))
    return counts, runs


def mask_inside(rect: Rect, runs: list) -> int:
    # Include a pixel when its center is inside the detection rectangle.
    left = math.ceil(rect.left - 0.5)
    right = math.ceil(rect.right - 0.5)
    return sum(max(0, min(right, x2) - max(left, x1)) for y, x1, x2 in runs
               if rect.top <= y + 0.5 < rect.bottom)


def pair_metrics(box: Box, segment: Segment, runs: list) -> tuple[float, float, float]:
    shared = box.rect.intersection(segment.rect)
    iou = shared / (box.rect.area + segment.rect.area - shared)
    if not shared:
        return iou, 0, 0
    coverage = mask_inside(box.rect, runs) / segment.area
    # A tight detection rectangle can have a greater area than the visible mask.
    affinity = 0.65 * iou + 0.35 * coverage * min(1, segment.rect.area / box.rect.area)
    return iou, coverage, affinity


def shortlist(image: str, boxes: list[Box], segments: list[Segment], runs: dict) -> list[dict]:
    def candidate(types, segment, selected_boxes, reason):
        return {"image": image, "type": types[0], "possible_types": types, "reason": reason,
                "detection": [{"class": box.name, "bbox": box.rect.xywh()} for box in selected_boxes],
                "panoptic": {"id": segment.id, "class": segment.name, "bbox": segment.rect.xywh()}}

    pairs = {(s, b): pair_metrics(b, s, runs[s.id]) for s in segments for b in boxes}
    entries = []
    for segment in segments:
        matched = sorted(boxes, key=lambda b: pairs[segment, b][2], reverse=True)
        same = [b for b in matched if b.name == segment.name]
        explained = [b for b in same if pairs[segment, b][0] >= 0.42 and pairs[segment, b][1] >= 0.89]
        parts = [b for b in same if pairs[segment, b][0] >= 0.12 and 0.15 <= pairs[segment, b][1] <= 0.82]
        merge = next(((a, b) for i, a in enumerate(parts) for b in parts[i + 1:]
                      if a.rect.intersection(b.rect) <= 0.33 * min(a.rect.area, b.rect.area)
                      and pairs[segment, a][1] + pairs[segment, b][1] >= 0.75), None)
        if not explained and merge:
            entries.append(candidate(["instance_merge"], segment, merge, "Hai box cùng lớp chia phần lớn pixel của segment"))
            continue
        if explained:
            continue
        if matched:
            best = matched[0]
            iou, coverage, affinity = pairs[segment, best]
            same_affinity = pairs[segment, same[0]][2] if same else 0
            other_affinity = max((pairs[s, best][2] for s in segments
                                  if s != segment and s.name == best.name), default=0)
            if (best.name != segment.name and iou >= 0.56 and coverage >= 0.78
                    and affinity >= max(same_affinity, other_affinity) + 0.08):
                entries.append(candidate(["class_swap", "category_swap"], segment, [best],
                                         f"Hai nguồn khác lớp, IoU {iou:.2f}, phủ mask {coverage:.0%}"))
                continue
        if same:
            best = same[0]
            iou, coverage, affinity = pairs[segment, best]
            ratio = best.rect.area / segment.rect.area
            other_affinity = max((pairs[s, best][2] for s in segments
                                  if s != segment and s.name == best.name), default=0)
            if (0.24 <= iou <= 0.81 and 0.20 <= coverage < 0.89 and 0.50 <= ratio <= 2.15
                    and segment.area >= 100 and other_affinity <= affinity + 0.05):
                entries.append(candidate(["bbox_drift"], segment, [best],
                                         f"Box cùng lớp chỉ phủ {coverage:.0%} pixel của segment"))
                continue
        if (segment.area >= 170 and min(segment.rect.right - segment.rect.left,
                                         segment.rect.bottom - segment.rect.top) >= 10
                and not any(pairs[segment, b][1] >= 0.48 or pairs[segment, b][0] >= 0.24 for b in same)):
            entries.append(candidate(["missing_box"], segment, [],
                                     "Segment thing đủ lớn, chưa tìm được box cùng lớp tương ứng"))
    return entries


def validate(delivery: Delivery, candidates: bool) -> tuple[list[dict], list[dict]]:
    panoptic = delivery.read_json("panoptic.json")
    categories = {c["id"]: c for c in panoptic["categories"]}
    annotations = {a["image_id"]: a["segments_info"] for a in panoptic["annotations"]}
    images = {Path(i["file_name"]).stem: i for i in panoptic["images"]}
    errors = {(finding["type"], finding["target"])
              for finding in find_duplicate_boxes(delivery.root) + find_thing_overlaps(delivery.root)}
    pending = []
    splits = defaultdict(set)
    for name, row in delivery.manifest.items():
        meta = delivery.metadata[name]
        splits[meta["scene_id"]].add(meta["split"])
        if meta["guideline_version"] != delivery.jobs[meta["job_id"]]["guideline"]:
            errors.add(("guideline_mismatch", name))
        paths = {kind: delivery.file(row[kind]) for kind in ("image", "label", "mask")}
        image_ok = paths["image"].is_file()
        if not image_ok:
            errors.add(("missing_image", name))
        if any(hashlib.sha256(path.read_bytes()).hexdigest() != row[f"{kind}_sha256"]
               for kind, path in paths.items() if path.is_file()):
            errors.add(("wrong_hash", name))

        entry = images[name]
        boxes, box_errors = detection(paths["label"], delivery.classes, entry["width"], entry["height"])
        errors.update((error, name) for error in box_errors)
        counts, runs = mask_runs(paths["mask"])
        segments = []
        for segment in annotations[entry["id"]]:
            category = categories.get(segment["category_id"])
            if category is None:
                errors.add(("invalid_category_id", name))
                continue
            if not category["isthing"] or segment.get("iscrowd"):
                continue
            sid = segment["id"]
            if counts[sid] and Rect.from_xywh(*segment["bbox"]).area:
                segments.append(Segment(sid, category["name"], Rect.from_xywh(*segment["bbox"]), counts[sid]))
        if candidates and image_ok and not box_errors and ("duplicate_box", name) not in errors:
            pending.extend(shortlist(name, boxes, segments, runs))

    errors.update(("scene_leak", scene) for scene, values in splits.items() if len(values) > 1)
    return [{"type": kind, "target": target} for kind, target in sorted(errors)], pending


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--candidates", type=Path)
    args = parser.parse_args()
    errors, candidates = validate(Delivery(args.delivery), args.candidates is not None)
    write_json(args.out, {"errors": errors})
    print(f"{len(errors)} lỗi luật → {args.out}")
    if args.candidates is not None:
        write_json(args.candidates, {"candidates": candidates})
        print(f"{len(candidates)} ứng viên / {len({c['image'] for c in candidates})} ảnh → {args.candidates}")


if __name__ == "__main__":
    main()
