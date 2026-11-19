#!/usr/bin/env python3
"""Chia ca review cho thành viên và ghi bảng chia vào <workdir>/assignments.csv.

Bảng chia là dữ liệu của từng lô, không nằm trong code, nên chạy được trên mọi
seed và trên đề ẩn (tên ảnh đã đổi). Người phụ trách review (TV4) có thể sửa
tay file CSV sau khi tạo; lệnh không ghi đè file đã có trừ khi dùng --force.

    python lab/split_review.py --workdir runs/r2412007
    python lab/split_review.py --workdir runs/de_an_work --hash-owner TV5
"""

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["image", "kind", "owner", "cross"]


def team_members(team_file=ROOT / "submission" / "TEAM.md"):
    """Đọc bảng thành viên trong TEAM.md, trả về {"TV1": "Họ tên", ...} theo thứ tự."""
    members = {}
    for line in Path(team_file).read_text(encoding="utf-8").splitlines():
        if not line.startswith("| TV"):
            continue
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) >= 2:
            members[cells[0]] = cells[1]
    return members


def hash_targets(rules):
    return sorted({row["target"] for row in rules if row["type"] == "wrong_hash"})


def auto_split(candidates, hashes, members, hash_owner="TV5"):
    """Chia đều theo tải: mỗi ca một người xem, ca bất đồng lớp thêm một người xem chéo.

    Ảnh lệch hash giao cho hash_owner (vai trò kiểm hash) nếu có trong nhóm.
    Thứ tự duyệt cố định theo mã ảnh nên mọi máy cho cùng một kết quả.
    """
    order = list(members)
    if not order:
        raise ValueError("TEAM.md chưa có thành viên.")
    load = {member: 0 for member in order}

    def lightest(exclude=()):
        pool = [m for m in order if m not in exclude]
        return min(pool, key=lambda m: (load[m], order.index(m)))

    rows = []
    for image in hashes:
        owner = hash_owner if hash_owner in load else lightest()
        load[owner] += 1
        rows.append({"image": image, "kind": "hash", "owner": owner, "cross": ""})
    semantic = []
    for case in sorted(candidates, key=lambda c: (c["image"], c["type"])):
        owner = lightest()
        load[owner] += 1
        row = {"image": case["image"], "kind": "semantic", "owner": owner, "cross": ""}
        semantic.append((row, len(case.get("possible_types", [])) > 1))
        rows.append(row)
    if len(order) > 1:
        for row, ambiguous in semantic:
            if ambiguous:
                row["cross"] = lightest(exclude={row["owner"]})
                load[row["cross"]] += 1
    return rows


def read_assignments(path):
    """Trả về {(kind, image): {"owner": ..., "cross": ...}} hoặc None nếu chưa có file."""
    path = Path(path)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {(row["kind"], row["image"]): {"owner": row.get("owner", "").strip(),
                                               "cross": row.get("cross", "").strip()}
                for row in csv.DictReader(handle)}


def write_assignments(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", type=Path, required=True, help="Thư mục có candidates.json và rules.json")
    parser.add_argument("--hash-owner", default="TV5", help="Người kiểm ảnh lệch hash (mặc định TV5)")
    parser.add_argument("--force", action="store_true", help="Ghi đè assignments.csv đã có")
    args = parser.parse_args()

    workdir = args.workdir
    target = workdir / "assignments.csv"
    members = team_members()
    if target.exists() and not args.force:
        print(f"Giữ nguyên bảng chia đã có: {target} (dùng --force để chia lại)")
        rows = [{"image": image, "kind": kind, **people}
                for (kind, image), people in read_assignments(target).items()]
    else:
        candidates = json.loads((workdir / "candidates.json").read_text(encoding="utf-8"))["candidates"]
        rules = json.loads((workdir / "rules.json").read_text(encoding="utf-8"))["errors"]
        rows = auto_split(candidates, hash_targets(rules), members, args.hash_owner)
        write_assignments(target, rows)
        print(f"Đã chia {len(rows)} ca → {target}")

    for member, name in members.items():
        own = [r["image"] + (" (hash)" if r["kind"] == "hash" else "") for r in rows if r["owner"] == member]
        cross = [r["image"] for r in rows if r["cross"] == member]
        text = ", ".join(own) or "—"
        if cross:
            text += " · xem chéo: " + ", ".join(cross)
        print(f"{member} {name}: {text}")


if __name__ == "__main__":
    main()
