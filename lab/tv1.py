#!/usr/bin/env python3
"""Prepare, collect human reviews and finish the T2412 practice handover."""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from build_handover import audit_review, read_hash_status
from review_server import ASSIGNMENTS, ROOT, Workspace
from trace_ticket import trace
from validate import write_json

sys.path.insert(0, str(ROOT / "scripts"))
import lineage
from export_submission import copy as export_files


def serialized(function):
    @wraps(function)
    def wrapped(workspace, *args, **kwargs):
        with workspace.writing():
            return function(workspace, *args, **kwargs)
    return wrapped


def command(script, *args, check=True):
    result = subprocess.run([sys.executable, str(ROOT / script), *map(str, args)],
                            cwd=ROOT, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if check and result.returncode:
        raise ValueError(f"{script} kết thúc với mã {result.returncode}.")
    return result


def backup(path):
    if path.exists():
        folder = path.parent / "tv1_backups"
        folder.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        shutil.copyfile(path, folder / f"{stamp}-{path.name}")


def prepare(run, seed):
    if not (run / "delivery/release.json").is_file():
        if not (ROOT / "data_source/coco_panoptic250/panoptic.json").is_file():
            command("scripts/download_public.py")
        # run_lab owns the first R-021 event for the canonical runs directory.
        if run != ROOT / "runs" / f"r{seed}":
            raise ValueError("Tạo lô mới tại runs/r<seed> để run_lab ghi đúng lineage.")
        command("scripts/run_lab.py", "--seeds", seed)
    workspace = Workspace(run)
    if not (run / "rules.json").is_file() or not (run / "candidates.json").is_file():
        command("validator/validate.py", run / "delivery", "--out", run / "rules.json",
                "--candidates", run / "candidates.json")
    if not (run / "trace.json").exists():
        write_json(run / "trace.json", trace(workspace.delivery))
    if not (run / "security.md").exists():
        shutil.copyfile(ROOT / "templates/security.md", run / "security.md")
    command("lab/prepare_review.py", run / "delivery", "--workdir", run)
    return workspace


@serialized
def import_reviews(workspace, sources):
    rows = workspace.csv("review_log.csv")
    candidates = workspace.candidates()
    members = workspace.members()
    count = 0
    for path in sources:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            incoming = list(csv.DictReader(handle))
        for row in incoming:
            if set(row) != {"image", "type", "verdict", "note"}:
                raise ValueError(f"{path}: CSV cần đúng 4 cột của review_log.")
            row = {key: (value or "").strip() for key, value in row.items()}
            if row["image"] not in workspace.delivery.manifest:
                raise ValueError(f"{path}: ảnh không thuộc lô {row['image']}.")
            if (row["type"] not in {"class_swap", "category_swap", "bbox_drift", "missing_box", "instance_merge"}
                    or row["verdict"] not in {"confirmed", "rejected"} or len(row["note"]) < 20
                    or not any(name in row["note"] for name in members.values())):
                raise ValueError(f"{path}: kết luận hoặc bằng chứng người xem chưa đủ cho {row['image']}.")
            case = next((c for c in candidates if c["image"] == row["image"]
                         and row["type"] in c["possible_types"]), None)
            types = case["possible_types"] if case else [row["type"]]
            indices = [i for i, old in enumerate(rows) if old["image"] == row["image"] and old["type"] in types]
            if len(indices) > 1:
                raise ValueError(f"Cần TV4 đối chiếu các dòng trùng của {row['image']}.")
            if indices:
                index = indices[0]
                old = rows[index]
                if old == row:
                    continue
                if old["verdict"]:
                    raise ValueError(f"Hai kết quả khác nhau cho {row['image']}. TV4 cần chốt trước khi nhập.")
                rows[index] = row
            else:
                rows.append(row)
            count += 1
    if count:
        workspace.replace_csv("review_log.csv", rows)
    print(f"Đã nhận {count} dòng mới. Giữ nguyên các kết luận đã có.")
    return count


@serialized
def import_hashes(workspace, sources):
    rows = workspace.csv("hash_review.csv")
    allowed = {case["image"] for case in workspace.state()["hash_cases"]}
    count = 0
    for path in sources:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            incoming = list(csv.DictReader(handle))
        for row in incoming:
            if set(row) != {"image", "status", "reviewer", "note"}:
                raise ValueError(f"{path}: cần 4 cột của hash_review.csv.")
            row = {key: (value or "").strip() for key, value in row.items()}
            if (row["image"] not in allowed or row["status"] not in {"intact", "damaged"}
                    or not row["note"] or not any(name in row["reviewer"] for name in workspace.members().values())):
                raise ValueError(f"{path}: kết quả kiểm ảnh hoặc người xem chưa hợp lệ.")
            indices = [i for i, old in enumerate(rows) if old["image"] == row["image"]]
            if len(indices) > 1:
                raise ValueError(f"Có dòng hash trùng cho {row['image']}.")
            if indices:
                old = rows[indices[0]]
                if old == row:
                    continue
                if old["status"]:
                    raise ValueError(f"Hai kết quả kiểm ảnh khác nhau cho {row['image']}.")
                rows[indices[0]] = row
            else:
                rows.append(row)
            count += 1
    if count:
        workspace.replace_csv("hash_review.csv", rows)
    print(f"Đã nhận {count} dòng kiểm ảnh mới.")
    return count


def status(workspace):
    state = workspace.state()
    pending = [
        {"image": case["image"], "owner": ASSIGNMENTS.get(case["image"], "TV4"),
         "possible_types": case["possible_types"]}
        for case in state["cases"] if not case["review"]
        or case["review"]["verdict"] not in {"confirmed", "rejected"}
        or len(case["review"]["note"].strip()) < 20
    ]
    hashes = [row["image"] for row in state["hash_cases"] if not row["review"]
              or row["review"]["status"] not in {"intact", "damaged"}
              or not row["review"]["reviewer"].strip() or not row["review"]["note"].strip()]
    rules = json.loads((workspace.run / "rules.json").read_text(encoding="utf-8"))["errors"]
    known = {(row["type"], row["target"]) for row in rules}
    known.update((row["type"], row["image"]) for row in workspace.csv("review_log.csv")
                 if row["verdict"] == "confirmed" and len(row["note"].strip()) >= 20)
    qc = len({target for _, target in known})
    security = workspace.run / "security.md"
    text = security.read_text(encoding="utf-8") if security.is_file() else ""
    result = {
        "release_id": state["release_id"], "run": workspace.run.name,
        "known_errors": len(known), "qc_targets": qc, "images": state["images_count"],
        "rate": qc / state["images_count"], "decision": "HOLD" if qc / state["images_count"] > .02 else "RELEASE_CANDIDATE",
        "review_saved": state["review_complete"], "review_total": len(state["cases"]),
        "pending_reviews": pending, "pending_hash_images": hashes,
        "security_needs_completion": not text or "<<" in text or len(re.findall(r"^## ", text, re.M)) < 3,
        "trace_exists": state["trace_exists"], "handover_exists": state["handover_exists"],
        "lineage": lineage.impact(workspace.run.parent, state["release_id"]),
    }
    print(f"QC đã biết {qc}/{state['images_count']} = {result['rate']:.1%} → {result['decision']}")
    print(f"Review đã lưu {state['review_complete']}/{len(state['cases'])}.")
    for case in pending:
        print(f"Chờ {case['owner']} xem ảnh {case['image']}.")
    for image in hashes:
        print(f"Chờ TV5 kiểm nội dung ảnh lệch hash {image}.")
    if result["security_needs_completion"]:
        print("Chờ TV7 hoàn tất security.md và ví dụ khuôn mặt do người xem xác nhận.")
    for row in result["lineage"]:
        print(f"{row['run_id']}: affected={row['affected']} action={row['action']}")
    return result


@serialized
def merge_known(workspace):
    backup(workspace.run / "errors.json")
    command("scripts/merge_review.py", "--rules", workspace.run / "rules.json",
            "--review", workspace.run / "review_log.csv", "--out", workspace.run / "errors.json")


def record_once(root, event):
    records = lineage.read(root)
    same = [row for row in records if row.get("event") == event["event"]
            and row.get("release_id") == event["release_id"]]
    if same:
        fields = ("parent",) if event["event"] == "release" else ("decision",)
        if any(any(row.get(field) != event.get(field) for field in fields) for row in same):
            raise ValueError("Lineage hiện có mâu thuẫn với sự kiện dự kiến.")
        return
    lineage.append(root, event)


def fingerprint(workspace):
    return {name: hashlib.sha256((workspace.run / name).read_bytes()).hexdigest()
            if (workspace.run / name).exists() else None
            for name in ("rules.json", "candidates.json", "review_log.csv", "hash_review.csv",
                         "trace.json", "security.md")}


@serialized
def finish(workspace, submission_root=None):
    current = status(workspace)
    if (current["pending_reviews"] or current["pending_hash_images"]
            or current["security_needs_completion"] or not current["trace_exists"]):
        raise ValueError("Chưa đủ đầu vào của người xem. Đã liệt kê ở trên.")
    lock = workspace.run / ".tv1-finalizing"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("Có lượt hoàn thiện đang chạy. Kiểm tiến trình trước khi gỡ khóa còn sót.")
    try:
        (lock / "pid").write_text(str(os.getpid()), encoding="utf-8")
        consumed = fingerprint(workspace)
        merge_known(workspace)
        errors = json.loads((workspace.run / "errors.json").read_text(encoding="utf-8"))["errors"]
        audit_review(workspace.run, errors)
        read_hash_status(workspace.run, errors, False)
        rid = current["release_id"]
        decision = "HOLD" if current["rate"] > .02 else "RELEASE"
        record_once(workspace.run.parent, {"event": "decision", "release_id": rid, "decision": decision})
        v2 = workspace.run / "handover" / f"{rid}_v2"
        if v2.exists():
            # A generated directory is retained for inspection on retries.
            archive = workspace.run / "tv1_backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            archive.mkdir(parents=True)
            shutil.move(str(v2), archive / v2.name)
            for extension in (".zip", ".sha256"):
                sibling = v2.with_suffix(extension)
                if sibling.exists():
                    shutil.move(str(sibling), archive / sibling.name)
        command("lab/build_handover.py", "--run", workspace.run)
        command("scripts/pack_release.py", v2)
        check = command("scripts/check_handover.py", "--run", workspace.run, check=False)
        failed = re.findall(r"\[FAIL\]\s+(H\d+b?)\b", check.stdout)
        if check.returncode and failed != ["H14"]:
            raise ValueError("Bộ kiểm còn lỗi ngoài lineage release. Xử lý các mục FAIL trước.")
        if failed == ["H14"] and decision != "HOLD":
            raise ValueError("H14 của bộ kiểm yêu cầu HOLD dù QC trong ngưỡng. Ghi nhận điểm này với giảng viên.")
        if consumed != fingerprint(workspace):
            raise ValueError("Đầu vào thay đổi trong lúc đóng gói. Chạy lại từ kết quả mới.")
        record_once(workspace.run.parent, {"event": "release", "release_id": f"{rid}_v2", "parent": rid})
        command("scripts/check_handover.py", "--run", workspace.run)
        target_root = Path(submission_root) if submission_root is not None else ROOT / "submission"
        target_root.mkdir(parents=True, exist_ok=True)
        destination = target_root / workspace.run.name
        export_files(workspace.run, destination)
        shutil.copyfile(workspace.run.parent / "lineage.jsonl", target_root / "lineage.jsonl")
        print(f"Đã kiểm đạt và xuất bài vào {destination}.")
    finally:
        shutil.rmtree(lock)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "status", "import-reviews", "import-hashes", "merge-known", "finish"])
    parser.add_argument("--run", type=Path, default=ROOT / "runs/r2412007")
    parser.add_argument("--seed", type=int, default=2412007)
    parser.add_argument("--source", type=Path, nargs="+", help="CSV kết quả người xem gửi về")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    workspace = prepare(run, args.seed) if args.action == "prepare" else Workspace(run)
    if args.action in {"import-reviews", "import-hashes"}:
        if not args.source:
            parser.error("Cần --source <CSV...> để nhận kết quả.")
        importer = import_reviews if args.action == "import-reviews" else import_hashes
        importer(workspace, args.source)
    elif args.action == "merge-known":
        merge_known(workspace)
    elif args.action == "finish":
        finish(workspace)
    result = status(workspace)
    if args.json_out:
        write_json(args.json_out, result)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
