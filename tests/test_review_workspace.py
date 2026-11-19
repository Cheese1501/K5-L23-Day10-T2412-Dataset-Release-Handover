"""Regression checks for CSV persistence, human review and local HTTP access."""

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from review_server import Conflict, Handler, ThreadingHTTPServer, Workspace
import pngutil


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name)
        delivery = self.run / "delivery"
        delivery.mkdir()
        files = {
            "manifest.json": {"items": {"sample": {"image": "images/sample.jpg", "mask": "masks/sample.png"}}},
            "metadata.json": {"items": []},
            "panoptic.json": {"images": [{"id": 1, "file_name": "sample.jpg", "width": 20, "height": 20}]},
            "release.json": {"release_id": "fixture"},
        }
        for name, value in files.items():
            (delivery / name).write_text(json.dumps(value))
        (delivery / "jobs.csv").write_text("job_id,annotator,reviewer,guideline\n")
        (delivery / "classes.txt").write_text("0 car\n")
        (delivery / "images").mkdir()
        (delivery / "masks").mkdir()
        pixels = bytes((0, 170, 187)) * 400
        pngutil.write_rgb(delivery / "images/sample.jpg", 20, 20, pixels)
        pngutil.write_rgb(delivery / "masks/sample.png", 20, 20, pixels)
        self.candidate = {
            "image": "sample", "type": "class_swap",
            "possible_types": ["class_swap", "category_swap"],
            "reason": "Test fixture", "detection": [],
            "panoptic": {"id": 1, "class": "car", "bbox": [0, 0, 20, 20]},
        }
        (self.run / "candidates.json").write_text(json.dumps({"candidates": [self.candidate]}))
        (self.run / "rules.json").write_text(json.dumps({"errors": [{"type": "wrong_hash", "target": "sample"}]}))
        (self.run / "review_log.csv").write_text("image,type,verdict,note\nsample,class_swap,,\n")
        (self.run / "hash_review.csv").write_text("image,status,reviewer,note\nsample,,,\n")
        self.workspace = Workspace(self.run)

    def body(self):
        return {
            "kind": "semantic", "image": "sample", "key": "sample|class_swap",
            "reviewer": "TV1", "type": "category_swap", "verdict": "confirmed",
            "note": "Temporary fixture for persistence checks only.",
            "seen": True,
            "revision": self.workspace.state()["review_revision"],
            "candidate_revision": self.workspace.state()["candidate_revision"],
        }

    def test_no_human_confirmation_creates_no_review(self):
        body = self.body()
        original = (self.run / "review_log.csv").read_bytes()
        body["seen"] = False
        with self.assertRaises(ValueError):
            self.workspace.save(body)
        self.assertEqual((self.run / "review_log.csv").read_bytes(), original)
        self.assertEqual(self.workspace.state()["review_complete"], 0)
        with self.assertRaises(ValueError):
            self.workspace.merge()

    def test_switching_type_preserves_csv_history(self):
        body = self.body()
        original = (self.run / "review_log.csv").read_bytes()
        result = self.workspace.save(body)
        self.assertEqual(result["state"]["review_complete"], 1)
        rows = self.workspace.csv("review_log.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["type"], "category_swap")
        self.assertIn("TV1", rows[0]["note"])
        backups = list((self.run / "review_backups").glob("*review_log.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        with self.assertRaises(Conflict):
            self.workspace.save(body)

    def test_hash_requires_known_image_and_named_reviewer(self):
        body = self.body()
        body.update(kind="hash", status="intact", revision=self.workspace.state()["hash_revision"])
        self.workspace.save(body)
        row, = self.workspace.csv("hash_review.csv")
        self.assertEqual(row["status"], "intact")
        self.assertTrue(row["reviewer"].startswith("TV1"))
        self.assertEqual(self.workspace.state()["hash_complete"], 1)

    def test_changed_candidate_list_blocks_stale_review(self):
        body = self.body()
        path = self.run / "candidates.json"
        path.write_text(path.read_text() + "\n")
        with self.assertRaises(Conflict):
            self.workspace.save(body)

    def test_second_reviewer_must_confirm_replacement(self):
        self.workspace.save(self.body())
        body = self.body()
        body["reviewer"] = "TV7"
        with self.assertRaises(Conflict):
            self.workspace.save(body)
        body["replace_review"] = True
        self.workspace.save(body)
        self.assertTrue(self.workspace.csv("review_log.csv")[0]["note"].startswith("TV7"))

    def test_merge_uses_original_script_after_complete_review(self):
        self.workspace.save(self.body())
        result = self.workspace.merge()
        findings = json.loads((self.run / "errors.json").read_text())["errors"]
        self.assertEqual({row["type"] for row in findings}, {"wrong_hash", "category_swap"})
        self.assertIn("message", result)

    def test_local_http_serves_assets_and_rejects_unsafe_writes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.workspace = self.workspace
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base + "/") as response:
            self.assertIn("Bàn làm việc TV1", response.read().decode())
        with urlopen(base + "/api/state") as response:
            state = json.load(response)
        body = self.body()
        invalid = Request(base + "/api/save", json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "Origin": "https://example.com",
            "X-Review-Token": state["token"],
        })
        with self.assertRaises(HTTPError) as error:
            urlopen(invalid)
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        request = Request(base + "/api/save", json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "Origin": base, "X-Review-Token": state["token"],
        })
        with urlopen(request) as response:
            self.assertEqual(json.load(response)["state"]["review_complete"], 1)
        for path in ("/download?name=../TEAM.md", "/asset/image?id=../secret", "/.git/config"):
            with self.assertRaises(HTTPError) as error:
                urlopen(base + path)
            self.assertEqual(error.exception.code, 404)
            error.exception.close()


if __name__ == "__main__":
    unittest.main()
