"""TV4: bảng chia ảnh theo dữ liệu của lô và trao đổi kết quả review giữa các máy."""

import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "scripts"))
import collect_reviews
import pngutil
from review_server import Workspace
from split_review import auto_split, read_assignments, team_members, write_assignments

MEMBERS = {f"TV{i}": f"Member {i}" for i in range(1, 8)}
NOTE = "Fixture note long enough for the twenty character rule."


def make_run(base, images=("img_a", "img_b", "img_c"), hash_image="img_h"):
    run = Path(base)
    delivery = run / "delivery"
    (delivery / "images").mkdir(parents=True)
    (delivery / "masks").mkdir()
    names = list(images) + [hash_image]
    pixels = bytes((0, 170, 187)) * 16
    for name in names:
        pngutil.write_rgb(delivery / f"images/{name}.jpg", 4, 4, pixels)
        pngutil.write_rgb(delivery / f"masks/{name}.png", 4, 4, pixels)
    files = {
        "manifest.json": {"items": {n: {"image": f"images/{n}.jpg", "mask": f"masks/{n}.png"} for n in names}},
        "metadata.json": {"items": []},
        "panoptic.json": {"images": [{"id": i, "file_name": f"{n}.jpg", "width": 4, "height": 4}
                                     for i, n in enumerate(names, 1)]},
        "release.json": {"release_id": "fixture"},
    }
    for name, value in files.items():
        (delivery / name).write_text(json.dumps(value))
    (delivery / "jobs.csv").write_text("job_id,annotator,reviewer,guideline\n")
    (delivery / "classes.txt").write_text("0 car\n")
    candidates = []
    for index, image in enumerate(images):
        ambiguous = index % 2 == 0
        candidates.append({
            "image": image, "type": "class_swap" if ambiguous else "bbox_drift",
            "possible_types": ["class_swap", "category_swap"] if ambiguous else ["bbox_drift"],
            "reason": "fixture", "detection": [],
            "panoptic": {"id": 1, "class": "car", "bbox": [0, 0, 4, 4]},
        })
    (run / "candidates.json").write_text(json.dumps({"candidates": candidates}))
    (run / "rules.json").write_text(json.dumps({"errors": [{"type": "wrong_hash", "target": hash_image}]}))
    (run / "review_log.csv").write_text("image,type,verdict,note\n"
                                        + "".join(f"{c['image']},{c['type']},,\n" for c in candidates))
    (run / "hash_review.csv").write_text(f"image,status,reviewer,note\n{hash_image},,,\n")
    return run, candidates


class SplitTest(unittest.TestCase):
    def test_team_file_lists_seven_members(self):
        self.assertEqual(list(team_members()), [f"TV{i}" for i in range(1, 8)])

    def test_split_is_balanced_deterministic_and_cross_checks_class_disputes(self):
        candidates = [{"image": f"img_{i:04d}", "type": "class_swap",
                       "possible_types": ["class_swap", "category_swap"]} for i in range(9)]
        rows = auto_split(candidates, ["img_hash"], MEMBERS)
        self.assertEqual(rows, auto_split(list(reversed(candidates)), ["img_hash"], MEMBERS))
        self.assertEqual(rows[0], {"image": "img_hash", "kind": "hash", "owner": "TV5", "cross": ""})
        load = {m: 0 for m in MEMBERS}
        for row in rows:
            load[row["owner"]] += 1
            if row["kind"] == "semantic":
                self.assertTrue(row["cross"])
                self.assertNotEqual(row["cross"], row["owner"])
                load[row["cross"]] += 1
        self.assertLessEqual(max(load.values()) - min(load.values()), 1)

    def test_single_type_case_has_no_cross_reviewer(self):
        rows = auto_split([{"image": "x", "type": "bbox_drift", "possible_types": ["bbox_drift"]}], [], MEMBERS)
        self.assertEqual(rows, [{"image": "x", "kind": "semantic", "owner": "TV1", "cross": ""}])


class WorkspaceAssignmentTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run, self.candidates = make_run(temporary.name)

    def test_every_case_has_an_owner_without_assignment_file(self):
        state = Workspace(self.run).state()
        self.assertTrue(all(c["owner"] for c in state["cases"] + state["hash_cases"]))

    def test_assignment_file_overrides_automatic_split(self):
        write_assignments(self.run / "assignments.csv", [
            {"image": "img_a", "kind": "semantic", "owner": "TV4", "cross": "TV7"},
            {"image": "img_h", "kind": "hash", "owner": "TV2", "cross": ""},
        ])
        state = Workspace(self.run).state()
        case = next(c for c in state["cases"] if c["image"] == "img_a")
        self.assertEqual((case["owner"], case["cross"]), ("TV4", "TV7"))
        self.assertEqual(state["hash_cases"][0]["owner"], "TV2")
        self.assertEqual(read_assignments(self.run / "assignments.csv")[("hash", "img_h")]["owner"], "TV2")

    def test_delivery_outside_run_directory(self):
        outside = self.run.parent / (self.run.name + "_delivery")
        shutil.move(str(self.run / "delivery"), outside)
        self.addCleanup(shutil.rmtree, outside, True)
        state = Workspace(self.run, outside).state()
        self.assertEqual(len(state["cases"]), len(self.candidates))


class CollectReviewsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        self.member_run, _ = make_run(base / "member")
        self.lead_run, _ = make_run(base / "lead")
        self.reviews = base / "reviews"

    def quiet(self, function, *args):
        with redirect_stdout(io.StringIO()) as output:
            code = function(*args)
        return code, output.getvalue()

    def save(self, workspace, member, image, kind_type, verdict="confirmed"):
        state = workspace.state()
        case = next(c for c in state["cases"] if c["image"] == image)
        workspace.save({"kind": "semantic", "image": image, "key": case["key"], "reviewer": member,
                        "type": kind_type, "verdict": verdict, "note": NOTE, "seen": True,
                        "revision": state["review_revision"], "candidate_revision": state["candidate_revision"]})

    def test_export_then_import_fills_lead_csv(self):
        member = Workspace(self.member_run)
        self.save(member, "TV3", "img_a", "category_swap")
        state = member.state()
        member.save({"kind": "hash", "image": "img_h", "reviewer": "TV5", "status": "intact",
                     "note": "Opened, content looks intact.", "seen": True,
                     "revision": state["hash_revision"], "candidate_revision": state["candidate_revision"]})
        self.assertEqual(self.quiet(collect_reviews.export, member, "TV3", self.reviews)[0], 0)
        self.assertEqual(self.quiet(collect_reviews.export, member, "TV5", self.reviews)[0], 0)
        self.assertTrue((self.reviews / "TV5_hash.csv").is_file())

        lead = Workspace(self.lead_run)
        original = (self.lead_run / "review_log.csv").read_bytes()
        self.quiet(collect_reviews.import_reviews, lead, self.reviews, True)
        self.assertEqual((self.lead_run / "review_log.csv").read_bytes(), original)
        code, _ = self.quiet(collect_reviews.import_reviews, lead, self.reviews, False)
        self.assertEqual(code, 0)
        row = next(r for r in lead.csv("review_log.csv") if r["image"] == "img_a")
        self.assertEqual((row["type"], row["verdict"]), ("category_swap", "confirmed"))
        self.assertTrue(row["note"].startswith("TV3 — "))
        self.assertEqual(len(lead.csv("review_log.csv")), 3)
        self.assertEqual(lead.csv("hash_review.csv")[0]["status"], "intact")
        self.assertTrue(any((self.lead_run / "review_backups").iterdir()))
        # Nhập lại lần nữa không đổi gì và không báo xung đột.
        before = (self.lead_run / "review_log.csv").read_bytes()
        self.assertEqual(self.quiet(collect_reviews.import_reviews, lead, self.reviews, False)[0], 0)
        self.assertEqual((self.lead_run / "review_log.csv").read_bytes(), before)

    def test_disagreement_is_reported_and_not_overwritten(self):
        lead = Workspace(self.lead_run)
        self.save(lead, "TV4", "img_a", "class_swap")
        self.reviews.mkdir()
        with (self.reviews / "TV7.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["image", "type", "verdict", "note"])
            writer.writerow(["img_a", "category_swap", "confirmed", "TV7 — Member 7 · " + NOTE])
            writer.writerow(["img_b", "bbox_drift", "rejected", "too short"])
            writer.writerow(["img_zz", "class_swap", "confirmed", "TV7 — " + NOTE])
        code, output = self.quiet(collect_reviews.import_reviews, lead, self.reviews, False)
        self.assertEqual(code, 1)
        self.assertIn("XUNG ĐỘT img_a", output)
        self.assertEqual(output.count("BỎ QUA"), 2)
        row = next(r for r in lead.csv("review_log.csv") if r["image"] == "img_a")
        self.assertEqual(row["type"], "class_swap")
        self.assertTrue(row["note"].startswith("TV4 — "))


    def test_member_export_replaces_their_own_older_row(self):
        lead = Workspace(self.lead_run)
        self.save(lead, "TV5", "img_b", "bbox_drift")
        self.reviews.mkdir()
        better = "TV5 — Member 5 · Box misses about 15px on the top and right edges."
        with (self.reviews / "TV5.csv").open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerows([["image", "type", "verdict", "note"],
                                          ["img_b", "bbox_drift", "confirmed", better]])
        code, output = self.quiet(collect_reviews.import_reviews, lead, self.reviews, False)
        self.assertEqual(code, 0, output)
        row = next(r for r in lead.csv("review_log.csv") if r["image"] == "img_b")
        self.assertEqual(row["note"], better)

if __name__ == "__main__":
    unittest.main()
