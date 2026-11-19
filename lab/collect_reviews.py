#!/usr/bin/env python3
"""Trao đổi kết quả xem ảnh giữa các máy qua submission/reviews/.

Thành viên xem ảnh trên máy mình bằng review_server.py rồi xuất phần của mình:
    python lab/collect_reviews.py --run runs/r2412007 --export TV3
    → submission/reviews/TV3.csv (ca gán nhãn), TV3_hash.csv (ca hash, nếu có)

TV4 nhập mọi file TV*.csv vào review_log.csv / hash_review.csv của lô:
    python lab/collect_reviews.py --run runs/r2412007 --import --dry-run
    python lab/collect_reviews.py --run runs/r2412007 --import

Khi nhập, dòng trống được điền, dòng giống hệt được bỏ qua, dòng cũ của cùng
một người được thay bằng bản người đó tự xuất. Ca đã có kết luận
khác (hai người xem ra kết quả khác nhau) được báo là xung đột và giữ nguyên để
TV4 đối chiếu với người xem; công cụ không tự chọn bên nào. Mọi lần ghi đều sao
lưu CSV cũ vào review_backups/ của lô.
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_server import CSV_FIELDS, ROOT, Workspace

SEMANTIC = CSV_FIELDS["review_log.csv"]
HASH = CSV_FIELDS["hash_review.csv"]


def read_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_rows(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def export(workspace, member, reviews):
    prefix = member + " — "
    semantic = [r for r in workspace.csv("review_log.csv")
                if r.get("verdict") and r.get("note", "").startswith(prefix)]
    hashes = [r for r in workspace.csv("hash_review.csv")
              if r.get("status") and r.get("reviewer", "").startswith(prefix)]
    written = []
    if semantic:
        write_rows(reviews / f"{member}.csv", SEMANTIC, semantic)
        written.append(f"{member}.csv ({len(semantic)} ca)")
    if hashes:
        write_rows(reviews / f"{member}_hash.csv", HASH, hashes)
        written.append(f"{member}_hash.csv ({len(hashes)} ca)")
    if not written:
        print(f"Chưa có kết luận nào mang tên {member} trong lô {workspace.run.name}.")
        return 1
    print("Đã xuất " + ", ".join(written) + f" vào {reviews}")
    return 0


def author(row):
    """Mã người xem ở đầu ghi chú hoặc cột reviewer, ví dụ "TV5"."""
    text = row.get("reviewer") or row.get("note") or ""
    return text.split(" — ", 1)[0] if " — " in text else ""


def merge_into(current, incoming, same_case, complete, source):
    """Gộp incoming vào current. Trả về (số dòng thêm/điền/cập nhật, danh sách xung đột).

    Dòng trống được điền. Dòng của cùng một người được thay bằng bản người đó tự
    xuất (họ sửa lại ghi chú). Kết luận khác của người khác là xung đột.
    """
    changed, conflicts = 0, []
    for row in incoming:
        indices = [i for i, existing in enumerate(current) if same_case(existing, row)]
        if not indices:
            current.append(row)
            changed += 1
        elif len(indices) > 1:
            conflicts.append(f"{row['image']}: CSV của lô có {len(indices)} dòng cho cùng ca ({source})")
        else:
            existing = current[indices[0]]
            same_author = author(existing) and author(existing) == author(row)
            if not complete(existing) or (same_author and existing != row):
                current[indices[0]] = row
                changed += 1
            elif any(existing.get(k, "") != row.get(k, "") for k in row):
                conflicts.append(f"{row['image']}: lô đang có {dict(existing)} — {source} gửi {dict(row)}")
    return changed, conflicts


def import_reviews(workspace, reviews, dry_run):
    state = workspace.state()
    cases = {c["image"]: c for c in state["cases"]}
    hash_images = {c["image"] for c in state["hash_cases"]}
    semantic, hashes, skipped = [], [], []
    files = sorted(reviews.glob("TV*.csv"))
    for path in files:
        fields, rows = read_rows(path)
        for row in rows:
            row = {k: (row.get(k) or "").strip() for k in fields}
            image = row.get("image", "")
            if fields[:len(SEMANTIC)] == SEMANTIC:
                case = cases.get(image)
                if case is None or row["type"] not in case["possible_types"]:
                    skipped.append(f"{path.name}: {image} {row.get('type')} không có trong hàng đợi của lô")
                elif row["verdict"] not in {"confirmed", "rejected"} or len(row["note"]) < 20:
                    skipped.append(f"{path.name}: {image} thiếu kết luận hoặc ghi chú dưới 20 ký tự")
                else:
                    semantic.append(({k: row[k] for k in SEMANTIC}, path.name))
            elif fields[:len(HASH)] == HASH:
                if image not in hash_images:
                    skipped.append(f"{path.name}: {image} không phải ảnh lệch hash của lô")
                elif row["status"] not in {"intact", "damaged"} or not row["reviewer"] or not row["note"]:
                    skipped.append(f"{path.name}: {image} thiếu trạng thái, người xem hoặc ghi chú")
                else:
                    hashes.append(({k: row[k] for k in HASH}, path.name))
            else:
                skipped.append(f"{path.name}: header không phải {SEMANTIC} hoặc {HASH}")
                break

    def same_semantic(existing, row):
        return existing["image"] == row["image"] and existing["type"] in cases[row["image"]]["possible_types"]

    log = workspace.csv("review_log.csv")
    hash_log = workspace.csv("hash_review.csv")
    changed = conflicts = 0
    report = []
    for rows, current, same, complete in (
            (semantic, log, same_semantic, lambda r: bool(r.get("verdict"))),
            (hashes, hash_log, lambda e, r: e["image"] == r["image"], lambda r: bool(r.get("status")))):
        for row, source in rows:
            added, found = merge_into(current, [row], same, complete, source)
            changed += added
            conflicts += len(found)
            report += ["XUNG ĐỘT " + item for item in found]
    for line in report + ["BỎ QUA " + item for item in skipped]:
        print(line)
    print(f"Đọc {len(files)} file, {len(semantic)} dòng gán nhãn, {len(hashes)} dòng hash. "
          f"Thêm/điền {changed}, xung đột {conflicts}, bỏ qua {len(skipped)}.")
    if not dry_run and changed:
        with workspace.writing():
            workspace.replace_csv("review_log.csv", log)
            workspace.replace_csv("hash_review.csv", hash_log)
        done = workspace.state()
        print(f"Đã ghi. Ca gán nhãn đủ kết luận {done['review_complete']}/{len(done['cases'])}, "
              f"hash {done['hash_complete']}/{len(done['hash_cases'])}.")
    elif dry_run:
        print("Chạy thử: chưa ghi gì.")
    return 1 if conflicts else 0


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--delivery", type=Path, help="Nếu delivery không nằm trong --run (đề ẩn)")
    parser.add_argument("--reviews", type=Path, default=ROOT / "submission" / "reviews",
                        help="Thư mục chứa TVx.csv (mặc định submission/reviews)")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--export", metavar="TVx", help="Xuất kết luận của một thành viên")
    action.add_argument("--import", dest="do_import", action="store_true", help="TV4 nhập mọi TV*.csv vào lô")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ báo kết quả nhập, không ghi")
    args = parser.parse_args()
    workspace = Workspace(args.run, args.delivery)
    if args.export:
        if args.export not in workspace.members():
            parser.error(f"{args.export} không có trong TEAM.md")
        return export(workspace, args.export, args.reviews)
    return import_reviews(workspace, args.reviews, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
