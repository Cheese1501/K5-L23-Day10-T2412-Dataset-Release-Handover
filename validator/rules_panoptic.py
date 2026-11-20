"""Panoptic mask rules for a delivery directory."""

from __future__ import annotations

import json
import sys
import zlib
from collections import Counter
from pathlib import Path
import struct


_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import pngutil


def find_thing_overlaps(delivery_dir: str | Path) -> list[dict[str, str]]:
    """Return one ``thing_overlap`` finding per affected image.

    For each non-crowd thing segment, compare its declared ``area`` with the
    number of mask pixels carrying that segment ID. Segment ID zero is the
    background and is excluded from counting.
    """
    delivery = Path(delivery_dir)
    panoptic_path = delivery / "panoptic.json"
    masks_dir = delivery / "masks"
    if not panoptic_path.is_file() or not masks_dir.is_dir():
        return []

    try:
        with panoptic_path.open("r", encoding="utf-8") as source:
            panoptic = json.load(source)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []

    if not isinstance(panoptic, dict):
        return []

    categories = panoptic.get("categories")
    images = panoptic.get("images")
    annotations = panoptic.get("annotations")
    if not all(isinstance(value, list) for value in (categories, images, annotations)):
        return []

    thing_category_ids = {
        category.get("id")
        for category in categories
        if isinstance(category, dict) and category.get("isthing")
    }
    image_names = {
        image.get("id"): Path(image["file_name"]).stem
        for image in images
        if isinstance(image, dict)
        and image.get("id") is not None
        and isinstance(image.get("file_name"), str)
    }

    findings: list[dict[str, str]] = []
    reported_targets: set[str] = set()
    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        image_id = annotation.get("image_id")
        target = image_names.get(image_id)
        mask_name = annotation.get("file_name")
        segments = annotation.get("segments_info")
        if (
            not target
            or target in reported_targets
            or not isinstance(mask_name, str)
            or not isinstance(segments, list)
        ):
            continue

        mask_path = masks_dir / Path(mask_name).name
        try:
            _, _, pixels = pngutil.read_rgb(mask_path)
        except (OSError, ValueError, IndexError, struct.error, zlib.error):
            continue

        pixel_counts: Counter[int] = Counter()
        try:
            for offset in range(0, len(pixels), 3):
                segment_id = pngutil.segment_id(pixels, offset)
                if segment_id != 0:
                    pixel_counts[segment_id] += 1
        except (IndexError, TypeError):
            continue

        overlap_found = False
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            if segment.get("category_id") not in thing_category_ids or segment.get("iscrowd"):
                continue
            try:
                segment_id = int(segment["id"])
                declared_area = int(segment["area"])
            except (KeyError, TypeError, ValueError):
                continue
            if declared_area > pixel_counts.get(segment_id, 0):
                overlap_found = True
                break

        if overlap_found:
            findings.append({"type": "thing_overlap", "target": target})
            reported_targets.add(target)

    return findings
