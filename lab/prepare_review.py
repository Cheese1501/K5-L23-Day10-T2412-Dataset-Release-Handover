#!/usr/bin/env python3
"""Create a local photo queue and CSV worklists for group members."""

import argparse
import csv
import html
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from validate import Delivery


def worklist(path, columns, rows):
    if path.exists():
        return
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


def image_url(delivery, image, base):
    relative = os.path.relpath(delivery.file(delivery.manifest[image]["image"]), base)
    return html.escape(quote(Path(relative).as_posix(), safe="/"))


def overlay(bbox, width, height, style, label):
    x, y, w, h = bbox
    return (f'<span class="{style}" title="{html.escape(label)}" style="left:{100*x/width}%;'
            f'top:{100*y/height}%;width:{100*w/width}%;height:{100*h/height}%"></span>')


def make_page(delivery, queue, hashes, target):
    dims = {Path(row["file_name"]).stem: (row["width"], row["height"])
            for row in delivery.read_json("panoptic.json")["images"]}
    cards = [
        '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" '
        'content="width=device-width, initial-scale=1"><title>Day 10 · Hàng đợi review</title>',
        '''<style>
body{font:17px system-ui,sans-serif;max-width:830px;margin:2rem auto;padding:0 1rem;color:#192333}
article{border-top:1px solid #b9c4cd;padding:1.25rem 0} figure{position:relative;margin:0;width:100%}
img{display:block;width:100%} span.det,span.pan{position:absolute;box-sizing:border-box;border:2px solid}
span.det{border-color:#ffb64b}span.pan{border-color:#43f1d2;border-style:dashed;pointer-events:none}
small{color:#344559}p{margin:.5rem 0}h3{margin:.2rem 0}
</style><h1>Hàng đợi review ảnh</h1>
<p>Cam liền là box detection. Xanh đứt là hộp bao segment panoptic.
Bấm vào ảnh để mở ảnh gốc, hoặc mở mask để kiểm tra hình dạng segment.
Ghi kết luận và tên người xem trong <code>review_log.csv</code>.
Nếu hai nguồn khác lớp, sửa cột <code>type</code> thành loại lỗi ứng với nguồn sai.</p>''',
        '<h2>Ảnh cần kiểm tra hash</h2><p>Ghi <code>intact</code> hoặc <code>damaged</code>, tên người xem và lý do trong '
        '<code>hash_review.csv</code>.</p><ul>',
    ]
    for image in hashes:
        cards.append(f'<li><a href="{image_url(delivery, image, target.parent)}">{html.escape(image)}</a></li>')
    cards.append(f"</ul><h2>{len(queue)} ứng viên</h2>")
    for candidate in queue:
        image = candidate["image"]
        width, height = dims[image]
        url = image_url(delivery, image, target.parent)
        mask = delivery.file(delivery.manifest[image]["mask"])
        mask_url = html.escape(quote(Path(os.path.relpath(mask, target.parent)).as_posix(), safe="/"))
        pan = candidate["panoptic"]
        detections = candidate["detection"]
        boxes = overlay(pan["bbox"], width, height, "pan", pan["class"])
        boxes += "".join(overlay(row["bbox"], width, height, "det", row["class"]) for row in detections)
        names = ", ".join(row["class"] for row in detections) or "không có box tương ứng"
        kinds = " / ".join(candidate["possible_types"])
        cards.append(
            f'<article><h3>{html.escape(image)} · {html.escape(kinds)}</h3>'
            f'<p>{html.escape(candidate["reason"])}</p>'
            f'<p><small>Detection: {html.escape(names)} · Panoptic: {html.escape(pan["class"])} '
            f'· <a href="{mask_url}" target="_blank" rel="noopener">Mở mask</a></small></p>'
            f'<figure><a href="{url}" target="_blank" rel="noopener"><img src="{url}" loading="lazy" '
            f'alt="{html.escape(image)}" width="{width}" height="{height}" style="height:auto"></a>{boxes}</figure></article>'
        )
    cards.append("</html>")
    target.write_text("\n".join(cards) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("delivery", type=Path)
    parser.add_argument("--workdir", type=Path, required=True,
                        help="Thư mục có rules.json và candidates.json")
    args = parser.parse_args()
    workdir = args.workdir.resolve()
    delivery = Delivery(args.delivery)
    queue = json.loads((workdir / "candidates.json").read_text(encoding="utf-8"))["candidates"]
    rules = json.loads((workdir / "rules.json").read_text(encoding="utf-8"))["errors"]
    hashes = sorted({row["target"] for row in rules if row["type"] == "wrong_hash"
                     and delivery.file(delivery.manifest[row["target"]]["image"]).is_file()})
    cases = sorted({(candidate["image"], candidate["type"]) for candidate in queue})
    worklist(workdir / "review_log.csv", ["image", "type", "verdict", "note"],
             [(image, kind, "", "") for image, kind in cases])
    worklist(workdir / "hash_review.csv", ["image", "status", "reviewer", "note"],
             [(image, "", "", "") for image in hashes])
    make_page(delivery, queue, hashes, workdir / "review.html")
    print(f"{len(cases)} ca cần review và {len(hashes)} ảnh cần kiểm hash → {workdir}")


if __name__ == "__main__":
    main()
