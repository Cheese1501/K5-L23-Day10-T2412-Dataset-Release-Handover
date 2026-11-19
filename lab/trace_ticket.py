#!/usr/bin/env python3
"""Find the affected images and people for a Day 10 lab ticket."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from validate import Delivery, write_json


def trace(delivery):
    changelog = delivery.file("guideline/changelog.md").read_text(encoding="utf-8")
    ticket = delivery.file("incoming/ticket.md").read_text(encoding="utf-8")
    change = re.search(r"(?mi)^\s*-\s*Lớp\s+`([^`]+)`.*?\((v\d+(?:\.\d+)+)\s+cho phép", changelog)
    scenes = set(re.findall(r"\bscene_[\w-]+\b", ticket))
    if change is None or not scenes:
        raise ValueError("Không đọc được lớp, phiên bản guideline cũ hoặc các cảnh từ tài liệu.")
    class_name, old_version = change.groups()
    if f"`{class_name}`" not in ticket:
        raise ValueError(f"Ticket và changelog không cùng lớp: {class_name}")
    class_id, = (number for number, name in delivery.classes.items() if name == class_name)

    result = {"tier_a": [], "tier_b": [], "notify": []}
    people = set()
    for image, item in sorted(delivery.manifest.items()):
        meta = delivery.metadata[image]
        job = delivery.jobs[meta["job_id"]]
        if job["guideline"] != old_version:
            continue
        label = delivery.file(item["label"]).read_text(encoding="utf-8")
        if any(float(line.split()[0]) == class_id for line in label.splitlines() if line.strip()):
            tier = "tier_a" if meta["scene_id"] in scenes else "tier_b"
            result[tier].append(image)
            people.update((job["annotator"], job["reviewer"]))
    result["notify"] = sorted(people)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = trace(Delivery(args.delivery))
    write_json(args.out, result)
    print(" · ".join(f"{key} {len(values)}" for key, values in result.items()))


if __name__ == "__main__":
    main()
