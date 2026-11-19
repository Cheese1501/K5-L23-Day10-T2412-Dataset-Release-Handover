"""Coordinator regression checks. All review conclusions here are synthetic."""

import contextlib
import csv
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab"))
import tv1
import pngutil
from review_server import Workspace
import test_review_workspace as fixtures


class CoordinatorTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.WorkspaceTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.temporary.cleanup)
        self.workspace = self.fixture.workspace

    def incoming(self, row):
        path = self.fixture.run / "incoming.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["image", "type", "verdict", "note"])
            writer.writeheader()
            writer.writerow(row)
        return path

    def test_import_is_idempotent_and_blocks_conflicting_verdict(self):
        row = {"image": "sample", "type": "category_swap", "verdict": "confirmed",
               "note": "TV1 — Lê Quang Khải · Synthetic fixture for importing only."}
        path = self.incoming(row)
        self.assertEqual(tv1.import_reviews(self.workspace, [path]), 1)
        before = (self.fixture.run / "review_log.csv").read_bytes()
        self.assertEqual(tv1.import_reviews(self.workspace, [path]), 0)
        row["verdict"] = "rejected"
        path = self.incoming(row)
        with self.assertRaises(ValueError):
            tv1.import_reviews(self.workspace, [path])
        self.assertEqual((self.fixture.run / "review_log.csv").read_bytes(), before)

    def test_finish_on_incomplete_review_writes_no_release(self):
        with self.assertRaises(ValueError):
            tv1.finish(self.workspace)
        self.assertFalse((self.fixture.run / "errors.json").exists())
        self.assertFalse((self.fixture.run / "handover").exists())
        self.assertFalse((self.fixture.run.parent / "lineage.jsonl").exists())

    def test_record_once_rejects_conflicting_parent(self):
        root = self.fixture.run / "event-root"
        event = {"event": "release", "release_id": "fixture_v2", "parent": "fixture"}
        tv1.record_once(root, event)
        tv1.record_once(root, event)
        self.assertEqual(len(tv1.lineage.read(root)), 1)
        with self.assertRaises(ValueError):
            tv1.record_once(root, {**event, "parent": "different"})

    def test_hash_import_preserves_existing_result_on_conflict(self):
        path = self.fixture.run / "incoming_hash.csv"
        path.write_text("image,status,reviewer,note\nsample,intact,TV5 — Đặng Trung Hiếu,Synthetic fixture only.\n")
        self.assertEqual(tv1.import_hashes(self.workspace, [path]), 1)
        self.assertEqual(tv1.import_hashes(self.workspace, [path]), 0)
        before = (self.fixture.run / "hash_review.csv").read_bytes()
        path.write_text(path.read_text().replace("intact", "damaged"))
        with self.assertRaises(ValueError):
            tv1.import_hashes(self.workspace, [path])
        self.assertEqual(before, (self.fixture.run / "hash_review.csv").read_bytes())

    def test_real_checker_and_export_on_synthetic_delivery_then_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root / "r999"
            delivery = run / "delivery"
            for subdir in ("images", "labels", "masks"):
                (delivery / subdir).mkdir(parents=True, exist_ok=True)
            manifest, metadata, images = {}, [], []
            for name in ("img_a", "img_b"):
                pngutil.write_rgb(delivery / "images" / f"{name}.jpg", 20, 20, bytes((1, 2, 3)) * 400)
                pngutil.write_rgb(delivery / "masks" / f"{name}.png", 20, 20, bytes((1, 0, 0)) * 400)
                (delivery / "labels" / f"{name}.txt").write_text("0 0.5 0.5 0.5 0.5\n")
                item = {kind: f"{folder}/{name}.{ext}" for kind, folder, ext in
                        (("image", "images", "jpg"), ("label", "labels", "txt"), ("mask", "masks", "png"))}
                for kind in ("image", "label", "mask"):
                    item[kind + "_sha256"] = hashlib.sha256((delivery / item[kind]).read_bytes()).hexdigest()
                manifest[name] = item
                metadata.append({"image": name, "scene_id": "scene_" + name, "split": "train",
                                 "job_id": "J01", "guideline_version": "v1.2"})
                images.append({"id": len(images) + 1, "file_name": name + ".jpg", "width": 20, "height": 20})
            def write(path, value):
                path.write_text(json.dumps(value))
            write(delivery / "manifest.json", {"items": manifest})
            write(delivery / "metadata.json", {"items": metadata})
            write(delivery / "panoptic.json", {"images": images, "annotations": [], "categories": []})
            rid = "lab250_" + hashlib.sha256((delivery / "manifest.json").read_bytes()
                                             + (delivery / "metadata.json").read_bytes()).hexdigest()[:12]
            write(delivery / "release.json", {
                "release_id": rid,
                "panoptic_sha256": hashlib.sha256((delivery / "panoptic.json").read_bytes()).hexdigest(),
            })
            (delivery / "classes.txt").write_text("0 car\n")
            (delivery / "jobs.csv").write_text("job_id,annotator,reviewer,guideline\nJ01,A01,Q01,v1.2\n")
            write(run / "rules.json", {"errors": []})
            write(run / "candidates.json", {"candidates": [{
                "image": "img_a", "type": "class_swap", "possible_types": ["class_swap", "category_swap"],
                "detection": [], "panoptic": {"id": 1}, "reason": "Synthetic fixture",
            }]})
            (run / "review_log.csv").write_text(
                "image,type,verdict,note\nimg_a,class_swap,confirmed,TV1 Synthetic fixture for completion pipeline only.\n")
            (run / "hash_review.csv").write_text("image,status,reviewer,note\n")
            write(run / "trace.json", {"tier_a": ["img_a"], "tier_b": ["img_b"], "notify": ["A01", "Q01"]})
            explanation = "Nội dung giả lập cho kiểm thử định dạng, mọi ảnh và kết luận ở đây đều là dữ liệu thử. " * 2
            (run / "security.md").write_text(
                f"## 1. USB\n{explanation}\n## 2. Năm việc\n{explanation}\n"
                f"## 3. Khuôn mặt\nHOLD, báo người phụ trách. img_b. {explanation}\n")
            tv1.lineage.append(root, {"event": "train", "release_id": rid, "run_id": "R-021"})
            workspace = Workspace(run)
            with contextlib.redirect_stdout(io.StringIO()) as output:
                tv1.finish(workspace, root / "export")
            self.assertIn("17 PASS, 0 FAIL", output.getvalue())
            artifact = run / "handover" / f"{rid}_v2.sha256"
            first_digest = artifact.read_text()
            exported = root / "export" / run.name
            self.assertTrue((exported / "handover" / f"{rid}_v2" / "images" / "img_b.jpg").is_file())
            self.assertFalse(list(exported.rglob("*.zip")))
            with contextlib.redirect_stdout(io.StringIO()):
                tv1.finish(workspace, root / "export")
            self.assertEqual(artifact.read_text(), first_digest)
            events = tv1.lineage.read(root)
            self.assertEqual(sum(row["event"] == "release" for row in events), 1)
            self.assertEqual(sum(row["event"] == "decision" for row in events), 1)
            self.assertFalse((run / ".tv1-finalizing").exists())


if __name__ == "__main__":
    unittest.main()
