"""Build ticket trace tiers from a delivery folder (never reads _private)."""
import argparse
import csv
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    delivery = args.delivery
    ticket = (delivery / "incoming" / "ticket.md").read_text(encoding="utf-8")
    changelog = (delivery / "guideline" / "changelog.md").read_text(encoding="utf-8")
    reported = set(re.findall(r"scene_\d+", ticket))
    versions = list(re.finditer(r"^##\s+(v[0-9]+(?:\.[0-9]+)*)\s*$", changelog, re.M))
    if len(versions) < 2:
        raise SystemExit("Changelog must include the changed guideline and its previous version")
    versions.sort(key=lambda entry: tuple(int(part) for part in entry.group(1)[1:].split(".")), reverse=True)
    latest = versions[0]
    previous = versions[1].group(1)
    next_heading = re.search(r"^##\s+", changelog[latest.end():], re.M)
    section_end = latest.end() + next_heading.start() if next_heading else len(changelog)
    changed_text = changelog[latest.end():section_end]
    match = re.search(r"Lớp\s+`([^`]+)`\s*:", changed_text)
    if not match:
        raise SystemExit("Could not identify the class changed in the latest guideline entry")
    class_name = match.group(1)
    classes = {}
    for line in (delivery / "classes.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            classes[parts[0]] = parts[1]
    class_ids = {class_id for class_id, name in classes.items() if name == class_name}
    jobs = {row["job_id"]: row for row in csv.DictReader((delivery / "jobs.csv").open(encoding="utf-8", newline=""))}
    metadata = json.loads((delivery / "metadata.json").read_text(encoding="utf-8"))["items"]
    matching = []
    for item in metadata:
        job = jobs.get(item["job_id"])
        if not job or job["guideline"] != previous:
            continue
        label = delivery / "labels" / f"{item['image']}.txt"
        if not label.is_file():
            continue
        has_class = any((fields := line.split()) and fields[0] in class_ids for line in label.read_text(encoding="utf-8").splitlines())
        if has_class:
            matching.append(item)
    tier_a = sorted(item["image"] for item in matching if item["scene_id"] in reported)
    tier_b = sorted(item["image"] for item in matching if item["scene_id"] not in reported)
    related_jobs = {item["job_id"] for item in matching}
    notify = sorted({jobs[j][key] for j in related_jobs for key in ("annotator", "reviewer")})
    result = {"tier_a": tier_a, "tier_b": tier_b, "notify": notify}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changed_class": class_name, "previous_guideline": previous, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

