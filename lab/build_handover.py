#!/usr/bin/env python3
"""Build a detection v2 from reviewed findings, or stage a draft from rules."""

import argparse
import csv
import json
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from validate import Delivery


REWORK = {"missing_image", "invalid_class", "bbox_out_of_bounds", "duplicate_box",
          "class_swap", "bbox_drift", "missing_box"}
PANOPTIC = {"invalid_category_id", "thing_overlap", "category_swap", "instance_merge"}


def csv_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit_review(run, errors):
    candidates = read_json(run / "candidates.json")["candidates"]
    review = csv_rows(run / "review_log.csv")
    for row in review:
        if row["verdict"] not in {"confirmed", "rejected"} or len(row["note"].strip()) < 20:
            raise ValueError(f"Ca review chưa có kết luận hoặc ghi chú đủ dài: {row['image']}, {row['type']}")
    recorded = {(row["image"], row["type"]) for row in review}
    for candidate in candidates:
        if not any((candidate["image"], kind) in recorded for kind in candidate["possible_types"]):
            raise ValueError(f"Ứng viên chưa được review: {candidate['image']}, {candidate['type']}")
    rules = read_json(run / "rules.json")["errors"]
    expected = {(item["type"], item["target"]) for item in rules}
    expected.update((row["type"], row["image"]) for row in review if row["verdict"] == "confirmed")
    if expected != {(item["type"], item["target"]) for item in errors}:
        raise ValueError("errors.json lệch rules.json hoặc review_log.csv. Chạy lại merge_review.py.")


def read_hash_status(run, errors, draft):
    required = {item["target"] for item in errors if item["type"] == "wrong_hash"}
    if draft or not required:
        return {}
    status = {}
    for row in csv_rows(run / "hash_review.csv"):
        if row["status"] in {"intact", "damaged"} and row["reviewer"].strip() and row["note"].strip():
            status[row["image"]] = row["status"]
    missing_images = {item["target"] for item in errors if item["type"] == "missing_image"}
    if missing := required - status.keys() - missing_images:
        raise ValueError("Cần hoàn thành hash_review.csv cho: " + ", ".join(sorted(missing)))
    return status


def populate(v2, delivery, errors, hashes, rid, draft):
    for dirname in ("images", "labels"):
        (v2 / dirname).mkdir()
    findings = defaultdict(set)
    for item in errors:
        findings[item["target"]].add(item["type"])
    allocations = defaultdict(Counter)
    for image in delivery.manifest:
        meta = delivery.metadata[image]
        allocations[meta["scene_id"]][meta["split"]] += 1
    splits = {}
    for scene, votes in allocations.items():
        ranking = votes.most_common()
        if len(ranking) > 1 and ranking[0][1] == ranking[1][1]:
            raise ValueError(f"Cảnh {scene} có số ảnh ngang nhau ở hai split, cần chốt split.")
        splits[scene] = ranking[0][0]

    label_counts = Counter()
    manifest = []
    rework = []
    trace = []
    guidelines = defaultdict(set)
    for image, item in sorted(delivery.manifest.items()):
        meta = delivery.metadata[image]
        job_id, scene = meta["job_id"], meta["scene_id"]
        job = delivery.jobs[job_id]
        owners = job["annotator"], job["reviewer"]
        kinds = findings[image]
        if kinds & REWORK:
            for kind in sorted(kinds & REWORK):
                rework.append((image, kind, *owners, "Bổ sung ảnh và kiểm nhãn" if kind == "missing_image"
                               else "Gán lại nhãn detection và kiểm lại"))
            continue
        if "wrong_hash" in kinds and hashes.get(image) != "intact":
            rework.append((image, "wrong_hash", *owners, "Đợi kiểm tra nội dung ảnh" if draft
                           else "Xin lại ảnh lành và kiểm nhãn đi kèm"))
            continue

        image_path, label_path = (delivery.file(item[kind]) for kind in ("image", "label"))
        for source, subdir in ((image_path, "images"), (label_path, "labels")):
            destination = v2 / subdir / source.name
            shutil.copyfile(source, destination)
            manifest.append((destination.relative_to(v2).as_posix(), sha256(destination.read_bytes()).hexdigest()))
        for line in label_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                label_counts[delivery.classes[int(float(line.split()[0]))]] += 1
        trace.append((image, scene, splits[scene], job_id, *owners, job["guideline"]))
        guidelines[job["guideline"]].add(job_id)

    write_csv(v2 / "manifest.csv", ["file", "sha256"], sorted(manifest))
    write_csv(v2 / "label_summary.csv", ["class", "count"],
              [*sorted(label_counts.items()), ("TOTAL", sum(label_counts.values()))])
    write_csv(v2 / "truyvet.csv", ["image", "scene_id", "split", "job_id", "annotator", "reviewer", "guideline"], trace)
    write_csv(v2 / "rework_queue.csv", ["image", "type", "annotator", "reviewer", "action"], rework)

    count = len({item["target"] for item in errors})
    denominator = len(delivery.manifest)
    rate = count / denominator
    decision = ("Hold — vượt ngưỡng 2%" if rate > 0.02 else "Release — trong ngưỡng 2%")
    if draft:
        decision = "Hold — chờ nhóm hoàn tất QC" if rate <= 0.02 else decision
    group_versions = ", ".join(f"{version} ({', '.join(sorted(ids))})" for version, ids in sorted(guidelines.items()))
    kept = {row[0] for row in trace}
    notes = remark_lines(delivery, findings, hashes, splits, kept, rework, draft)
    fixed = sum(1 for line in notes if line.startswith(("Hash ", "Guideline ", "Split ")))
    rework_images = len({row[0] for row in rework})
    v2_status = (f"Hold — bản nháp chờ nhóm xem ảnh và chốt hàng đợi; tạm tách {rework_images} ảnh"
                 if draft else
                 f"Release — tách {rework_images} ảnh lỗi detection/ảnh hỏng sang rework_queue.csv, "
                 f"sửa {fixed} mục hash/guideline/split ngay trong v2 (chi tiết ở Ghi chú)")
    (v2 / "README.txt").write_text(
        f"Release: {rid}_v2\nParent: {rid}\nSố ảnh: {len(trace)}\nSố nhãn: {sum(label_counts.values())}\n"
        f"Guideline: {group_versions}\nQC v1: {count}/{denominator} = {rate:.1%}\n"
        f"Kết luận v1: {decision}\nKết luận v2: {v2_status}\nGhi chú:\n"
        + "".join(f"  - {line}\n" for line in notes),
        encoding="utf-8",
    )
    return len(trace), len(rework)


def remark_lines(delivery, findings, hashes, splits, kept, rework, draft):
    """Ghi chú cụ thể: sửa gì trong v2, vì sao, ai nhận rework, báo team panoptic."""
    lines = []
    by_type = defaultdict(list)
    for target, kinds in findings.items():
        for kind in kinds:
            by_type[kind].append(target)

    # Hash: chỉ giữ ảnh khi người xem đã mở và ghi intact trong hash_review.csv.
    sha_owner = {}
    for image, item in delivery.manifest.items():
        path = delivery.file(item["image"])
        if path.is_file():
            sha_owner[sha256(path.read_bytes()).hexdigest()] = image
    for image in sorted(by_type["wrong_hash"]):
        if image not in kept:
            reason = ("tạm tách, chờ người xem mở ảnh" if draft and image not in hashes
                      else "ảnh hỏng khi mở kiểm (hash_review.csv), chuyển rework")
            lines.append(f"Hash {image}: sha256 trong manifest v1 không khớp file; {reason}.")
            continue
        old = delivery.manifest[image].get("image_sha256", "")
        twin = sha_owner.get(old)
        cause = f" (hash cũ là hash của {twin}.jpg, manifest v1 ghi nhầm)" if twin and twin != image else ""
        lines.append(f"Hash {image}: mở ảnh kiểm thấy còn nguyên (hash_review.csv){cause}; "
                     "giữ ảnh, manifest.csv v2 ghi sha256 tính lại từ file thật.")

    # Guideline: lấy theo job trong jobs.csv, vì guideline ghi ở ảnh chính là chỗ sai.
    for image in sorted(by_type["guideline_mismatch"]):
        if image not in kept:
            continue
        meta = delivery.metadata[image]
        job = meta["job_id"]
        lines.append(f"Guideline {image}: metadata v1 ghi {meta.get('guideline_version', '?')}, "
                     f"job {job} trong jobs.csv là {delivery.jobs[job]['guideline']}; "
                     "truyvet.csv ghi theo job vì ảnh được gán theo guideline của job.")

    # Split: cả cảnh về một split (đa số ảnh), tránh ảnh gần giống nhau lọt giữa train và val/test.
    for scene in sorted(by_type["scene_leak"]):
        moved = [image for image in sorted(delivery.manifest)
                 if image in kept and delivery.metadata[image]["scene_id"] == scene
                 and delivery.metadata[image]["split"] != splits[scene]]
        detail = ", ".join(f"{image} ({delivery.metadata[image]['split']} → {splits[scene]})" for image in moved)
        lines.append(f"Split {scene}: đưa cả cảnh về {splits[scene]} theo đa số ảnh của cảnh; "
                     f"đổi {detail or 'không ảnh nào còn trong v2'}. Lý do: ảnh cùng cảnh nằm ở hai split làm rò dữ liệu.")

    # Rework: tách khỏi v2, giao lại đúng người gán và người kiểm của job.
    owners = Counter((row[2], row[3]) for row in rework)
    if rework:
        kinds = Counter(row[1] for row in rework)
        lines.append(f"Rework: tách {len({row[0] for row in rework})} ảnh khỏi v2 ("
                     + ", ".join(f"{kind} {n}" for kind, n in sorted(kinds.items())) + "); giao lại "
                     + ", ".join(f"{a}/{q}: {n} ảnh" for (a, q), n in sorted(owners.items()))
                     + " (người gán/người kiểm theo jobs.csv), xem rework_queue.csv.")

    # Panoptic: nhãn detection vẫn đúng nên ảnh ở lại v2; báo team panoptic sửa mask.
    panoptic = [f"{image} ({', '.join(sorted(kinds & PANOPTIC))})"
                for image, kinds in sorted(findings.items()) if kinds & PANOPTIC]
    if panoptic:
        lines.append("Báo team panoptic (ảnh ở lại v2 vì nhãn detection không sai): " + "; ".join(panoptic) + ".")
    if draft:
        lines.append("Bản nháp: QC v1 mới gồm lỗi luật, chưa có lỗi gán nhãn từ review ảnh.")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--draft", action="store_true", help="Dùng lỗi luật để dựng bản nháp trong draft/")
    args = parser.parse_args()
    run = args.run
    delivery = Delivery(run / "delivery")
    rid = delivery.read_json("release.json")["release_id"]
    errors = read_json(run / ("rules.json" if args.draft else "errors.json"))["errors"]
    if not args.draft:
        audit_review(run, errors)
    hashes = read_hash_status(run, errors, args.draft)
    folder = run / ("draft" if args.draft else "handover")
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"{rid}_v2"
    if destination.exists():
        parser.error(f"{destination} đã tồn tại. Hãy chuyển thư mục cũ sang vị trí lưu trước khi tạo lại.")
    with tempfile.TemporaryDirectory(dir=folder) as temporary:
        v2 = Path(temporary) / destination.name
        v2.mkdir()
        images, rework = populate(v2, delivery, errors, hashes, rid, args.draft)
        v2.rename(destination)
    print(f"{destination} · {images} ảnh · {rework} dòng rework")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError) as error:
        sys.exit(str(error))
