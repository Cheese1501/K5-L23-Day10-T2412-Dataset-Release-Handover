"""Detection label rules for a delivery directory."""

from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import pngutil


def find_duplicate_boxes(delivery_dir: str | Path) -> list[dict[str, str]]:
    """Return one ``duplicate_box`` finding per affected image.

    YOLO coordinates are normalized to the image dimensions. The matching
    mask PNG supplies those dimensions, so no image-decoding dependency is
    needed. Box sizes and centers are rounded to pixel coordinates before
    comparison. Same-class boxes with identical pixel sizes are duplicates
    when their centers are identical or differ by at most two pixels on each
    axis.
    """
    delivery = Path(delivery_dir)
    labels_dir = delivery / "labels"
    masks_dir = delivery / "masks"
    findings: list[dict[str, str]] = []

    if not labels_dir.is_dir() or not masks_dir.is_dir():
        return findings

    for label_path in sorted(labels_dir.glob("*.txt")):
        mask_path = masks_dir / f"{label_path.stem}.png"
        try:
            width, height, _ = pngutil.read_rgb(mask_path)
        except (OSError, ValueError, IndexError, struct.error, zlib.error):
            # Without the corresponding mask dimensions, normalized boxes
            # cannot be compared reliably in pixels.
            continue
        if width <= 0 or height <= 0:
            continue

        groups: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
        try:
            rows = label_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue

        for row in rows:
            fields = row.split()
            if len(fields) != 5:
                continue
            try:
                class_id = int(fields[0])
                cx, cy, box_width, box_height = map(float, fields[1:])
            except ValueError:
                continue
            if not all(math.isfinite(value) for value in (cx, cy, box_width, box_height)):
                continue

            pixel_width = round(box_width * width)
            pixel_height = round(box_height * height)
            pixel_cx = round(cx * width)
            pixel_cy = round(cy * height)
            groups.setdefault((class_id, pixel_width, pixel_height), []).append(
                (pixel_cx, pixel_cy)
            )

        duplicate_found = False
        for centers in groups.values():
            for index, (cx, cy) in enumerate(centers):
                for other_cx, other_cy in centers[index + 1 :]:
                    if max(abs(cx - other_cx), abs(cy - other_cy)) <= 2:
                        duplicate_found = True
                        break
                if duplicate_found:
                    break
            if duplicate_found:
                break

        if duplicate_found:
            findings.append({"type": "duplicate_box", "target": label_path.stem})

    return findings
