#!/usr/bin/env python3
"""Local review workspace. Run from the repository with --run runs/r2412007."""

import argparse
import csv
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "validator"))
from validate import Delivery

ROOT = Path(__file__).resolve().parents[1]
UI = Path(__file__).with_name("review_ui")
ASSIGNMENTS = {
    "000000009891": "TV1", "000000018491": "TV2", "000000006012": "TV3",
    "000000023023": "TV4", "000000023781": "TV5", "000000025386": "TV6",
}
CSV_FIELDS = {
    "review_log.csv": ["image", "type", "verdict", "note"],
    "hash_review.csv": ["image", "status", "reviewer", "note"],
}
DOWNLOADS = {"rules.json", "candidates.json", "errors.json", "review_log.csv",
             "hash_review.csv", "trace.json", "security.md"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def revision(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


class Conflict(ValueError):
    pass


class Workspace:
    def __init__(self, run):
        self.run = run.resolve()
        self.delivery = Delivery(self.run / "delivery")
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)

    def members(self):
        rows = (ROOT / "submission" / "TEAM.md").read_text(encoding="utf-8").splitlines()
        return {cells[0]: cells[1] for line in rows
                if line.startswith("| TV")
                and len(cells := [cell.strip() for cell in line.split("|")[1:-1]]) >= 2}

    def candidates(self):
        return read_json(self.run / "candidates.json")["candidates"]

    def csv(self, filename):
        path = self.run / filename
        if not path.exists():
            return []
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def replace_csv(self, filename, rows):
        path = self.run / filename
        if path.exists():
            backups = self.run / "review_backups"
            backups.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            shutil.copyfile(path, backups / f"{stamp}-{secrets.token_hex(4)}-{filename}")
        fd, temporary = tempfile.mkstemp(prefix=".review-", dir=self.run)
        try:
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS[filename])
                writer.writeheader()
                writer.writerows(rows)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def state(self):
        with self.lock:
            reviews = self.csv("review_log.csv")
            hashes = self.csv("hash_review.csv")
            images = {Path(row["file_name"]).stem: row
                      for row in self.delivery.read_json("panoptic.json")["images"]}
            cases = []
            for row in self.candidates():
                matches = [r for r in reviews if r["image"] == row["image"]
                           and r["type"] in row["possible_types"]]
                cases.append({
                    **row, "key": row["image"] + "|" + row["type"],
                    "owner": ASSIGNMENTS.get(row["image"], ""),
                    "width": images[row["image"]]["width"], "height": images[row["image"]]["height"],
                    "review": matches[0] if len(matches) == 1 else None,
                })
            rules = read_json(self.run / "rules.json")["errors"]
            hash_images = sorted({r["target"] for r in rules if r["type"] == "wrong_hash"
                                  and r["target"] in self.delivery.manifest
                                  and self.delivery.file(self.delivery.manifest[r["target"]]["image"]).is_file()})
            hash_cases = [{"image": image, "owner": "TV5",
                           "review": next((r for r in hashes if r["image"] == image), None)}
                          for image in hash_images]
            complete = sum(bool(c["review"] and c["review"]["verdict"] in {"confirmed", "rejected"}
                                and len(c["review"]["note"].strip()) >= 20) for c in cases)
            hash_complete = sum(bool(c["review"] and c["review"]["status"] in {"intact", "damaged"}
                                     and c["review"]["reviewer"].strip() and c["review"]["note"].strip())
                                for c in hash_cases)
            release_id = self.delivery.read_json("release.json")["release_id"]
            count = len({r["target"] for r in rules})
            total = len(self.delivery.manifest)
            handover = self.run / "handover" / f"{release_id}_v2"
            return {
                "members": self.members(), "cases": cases, "hash_cases": hash_cases,
                "token": self.token, "run": self.run.name, "release_id": release_id,
                "rules_count": count, "images_count": total, "rate": count / total,
                "review_complete": complete, "hash_complete": hash_complete,
                "review_revision": revision(self.run / "review_log.csv"),
                "hash_revision": revision(self.run / "hash_review.csv"),
                "candidate_revision": revision(self.run / "candidates.json"),
                "handover_exists": handover.is_dir(),
                "trace_exists": (self.run / "trace.json").is_file(),
                "security_exists": (self.run / "security.md").is_file(),
            }

    def save(self, body):
        with self.lock:
            if body.get("seen") is not True:
                raise ValueError("Cần xác nhận bạn đã trực tiếp mở và xem ảnh.")
            member = body.get("reviewer", "")
            if member not in self.members():
                raise ValueError("Chọn thành viên đã trực tiếp xem ảnh.")
            if not isinstance(body.get("note"), str):
                raise ValueError("Ghi chú phải là văn bản.")
            note = body["note"].strip()
            if len(note) < 20:
                raise ValueError("Ghi ít nhất 20 ký tự mô tả điều bạn nhìn thấy.")
            image = body.get("image")
            kind = body.get("kind")
            filename = "hash_review.csv" if kind == "hash" else "review_log.csv"
            if body.get("revision") != revision(self.run / filename):
                raise Conflict("CSV vừa thay đổi. Tải lại dữ liệu rồi kiểm tra trước khi lưu tiếp.")
            if body.get("candidate_revision") != revision(self.run / "candidates.json"):
                raise Conflict("Danh sách ứng viên vừa thay đổi. Tải lại trước khi lưu.")

            rows = self.csv(filename)
            if kind == "hash":
                allowed = {row["image"] for row in self.state()["hash_cases"]}
                if image not in allowed or body.get("status") not in {"intact", "damaged"}:
                    raise ValueError("Ảnh hoặc trạng thái hash không hợp lệ.")
                new = {"image": image, "status": body["status"],
                       "reviewer": f"{member} — {self.members()[member]}", "note": note}
                indices = [i for i, row in enumerate(rows) if row["image"] == image]
            elif kind == "semantic":
                case = next((c for c in self.candidates()
                             if c["image"] == image and c["image"] + "|" + c["type"] == body.get("key")), None)
                if case is None or body.get("type") not in case["possible_types"]:
                    raise ValueError("Ảnh hoặc loại lỗi không có trong hàng đợi.")
                if body.get("verdict") not in {"confirmed", "rejected"}:
                    raise ValueError("Chọn một kết luận trước khi lưu.")
                new = {"image": image, "type": body["type"], "verdict": body["verdict"],
                       "note": f"{member} — {self.members()[member]} · {note}"}
                indices = [i for i, row in enumerate(rows) if row["image"] == image
                           and row["type"] in case["possible_types"]]
            else:
                raise ValueError("Loại yêu cầu không hợp lệ.")
            if len(indices) > 1:
                raise Conflict("Có nhiều dòng trùng cho ca này. Nhờ TV4 đối chiếu CSV trước.")
            if indices:
                previous = rows[indices[0]]
                existing = previous.get("status") if kind == "hash" else previous.get("verdict")
                owner_text = previous.get("reviewer", "") if kind == "hash" else previous.get("note", "")
                if existing and not owner_text.startswith(member + " — ") and body.get("replace_review") is not True:
                    raise Conflict("Ca này có kết quả của người khác. Cần xác nhận trước khi thay kết luận.")
                rows[indices[0]] = new
            else:
                rows.append(new)
            self.replace_csv(filename, rows)
            return {"message": f"Đã lưu {image} vào {filename}.", "state": self.state()}

    def check(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_handover.py"),
                                 "--run", str(self.run)], cwd=ROOT, capture_output=True, text=True,
                                timeout=120)
        return {"exit_code": result.returncode, "output": result.stdout + result.stderr}

    def merge(self):
        with self.lock:
            state = self.state()
            if state["review_complete"] != len(state["cases"]):
                raise ValueError("Cần hoàn thành kết luận của mọi ứng viên trước khi gộp.")
            output = self.run / "errors.json"
            if output.exists():
                backups = self.run / "review_backups"
                backups.mkdir(exist_ok=True)
                shutil.copyfile(output, backups / f"{secrets.token_hex(12)}-errors.json")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/merge_review.py"),
                                     "--rules", str(self.run / "rules.json"),
                                     "--review", str(self.run / "review_log.csv"),
                                     "--out", str(output)], cwd=ROOT, capture_output=True, text=True,
                                    timeout=30)
            if result.returncode:
                raise ValueError(result.stdout + result.stderr)
            return {"message": result.stdout.strip(), "state": self.state()}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, data, mime="application/json; charset=utf-8", attachment=None):
        payload = json.dumps(data, ensure_ascii=False).encode() if isinstance(data, dict) else data
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "script-src 'self'; frame-ancestors 'none'; form-action 'self'")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
        self.end_headers()
        self.wfile.write(payload)

    def trusted_host(self):
        return self.headers.get("Host") in {
            f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self.trusted_host():
            self.send(403, {"error": "Host không hợp lệ."})
            return
        query = urlsplit(self.path)
        params = parse_qs(query.query)
        workspace = self.server.workspace
        try:
            if query.path == "/api/state":
                self.send(200, workspace.state())
            elif query.path == "/api/health":
                self.send(200, {"run": str(workspace.run), "service": "day10-review"})
            elif query.path in {"/", "/app.js", "/style.css"}:
                filename, mime = {"/": ("index.html", "text/html; charset=utf-8"),
                                  "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                                  "/style.css": ("style.css", "text/css; charset=utf-8")}[query.path]
                self.send(200, (UI / filename).read_bytes(), mime)
            elif query.path in {"/asset/image", "/asset/mask"}:
                image = params.get("id", [""])[0]
                item = workspace.delivery.manifest[image]
                kind = "image" if query.path == "/asset/image" else "mask"
                mime = "image/jpeg" if kind == "image" else "image/png"
                self.send(200, workspace.delivery.file(item[kind]).read_bytes(), mime)
            elif query.path == "/download":
                filename = params.get("name", [""])[0]
                if filename not in DOWNLOADS:
                    raise KeyError(filename)
                self.send(200, (workspace.run / filename).read_bytes(),
                          "application/octet-stream", filename)
            else:
                self.send(404, {"error": "Không có trang này."})
        except (KeyError, FileNotFoundError):
            self.send(404, {"error": "File hoặc ảnh chưa có."})
        except (ValueError, OSError) as error:
            self.send(400, {"error": str(error)})

    def do_POST(self):
        origin = self.headers.get("Origin")
        allowed = {f"http://127.0.0.1:{self.server.server_port}",
                   f"http://localhost:{self.server.server_port}"}
        if (not self.trusted_host() or origin not in allowed
                or self.headers.get("X-Review-Token") != self.server.workspace.token):
            self.send(403, {"error": "Yêu cầu không xuất phát từ màn hình review trên máy."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("Yêu cầu quá dài hoặc trống.")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Nội dung yêu cầu không hợp lệ.")
            with self.server.workspace.lock:
                if self.path == "/api/save":
                    result = self.server.workspace.save(body)
                elif self.path == "/api/merge":
                    result = self.server.workspace.merge()
                elif self.path == "/api/check":
                    result = self.server.workspace.check()
                else:
                    self.send(404, {"error": "Không có thao tác này."})
                    return
            self.send(200, result)
        except Conflict as error:
            self.send(409, {"error": str(error)})
        except (ValueError, OSError, subprocess.TimeoutExpired) as error:
            self.send(400, {"error": str(error)})

    def log_message(self, format, *args):
        print(format % args, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "runs/r2412007")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    workspace = Workspace(args.run)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        try:
            with urlopen(f"http://127.0.0.1:{args.port}/api/health", timeout=2) as response:
                health = json.load(response)
            if health.get("service") == "day10-review" and health.get("run") == str(workspace.run):
                url = f"http://127.0.0.1:{args.port}/"
                print(f"Công cụ đã chạy: {url}", flush=True)
                if args.open:
                    webbrowser.open(url)
                return
        except (OSError, ValueError):
            pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server.workspace = workspace
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"TV1 review: {url}", flush=True)
    print("CSV lưu trong " + str(workspace.run), flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
