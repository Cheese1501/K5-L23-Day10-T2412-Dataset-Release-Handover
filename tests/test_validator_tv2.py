"""Integration checks for the two TV2 rule modules using synthetic deliveries."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from validator import validate
from validator.rules_detection import find_duplicate_boxes
from validator.rules_panoptic import find_thing_overlaps
from scripts import pngutil


class TV2IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.delivery = Path(self.temporary.name)
        for folder in ("images", "labels", "masks"):
            (self.delivery / folder).mkdir()
        pngutil.write_rgb(self.delivery / "images/example.jpg", 20, 20, bytes((20, 40, 60)) * 400)
        pngutil.write_rgb(self.delivery / "masks/example.png", 20, 20, bytes((1, 0, 0)) * 400)
        self.label("0 .5 .5 .5 .5\n")
        self.panoptic = {
            "categories": [{"id": 1, "name": "car", "isthing": 1}],
            "images": [{"id": 1, "file_name": "example.jpg", "width": 20, "height": 20}],
            "annotations": [{"image_id": 1, "file_name": "example.png",
                             "segments_info": [{"id": 1, "category_id": 1, "area": 400,
                                                "bbox": [0, 0, 20, 20], "iscrowd": 0}]}],
        }
        self.json("panoptic.json", self.panoptic)
        self.json("metadata.json", {"items": [{"image": "example", "scene_id": "scene_test",
                   "split": "train", "job_id": "J01", "guideline_version": "v1.2"}]})
        (self.delivery / "jobs.csv").write_text("job_id,annotator,reviewer,guideline\nJ01,A01,Q01,v1.2\n")
        (self.delivery / "classes.txt").write_text("0 car\n")
        self.manifest()

    def label(self, text):
        (self.delivery / "labels/example.txt").write_text(text)

    def json(self, name, data):
        (self.delivery / name).write_text(json.dumps(data))

    def manifest(self):
        item = {"image": "images/example.jpg", "label": "labels/example.txt", "mask": "masks/example.png"}
        for kind, path in list(item.items()):
            item[kind + "_sha256"] = hashlib.sha256((self.delivery / path).read_bytes()).hexdigest()
        self.json("manifest.json", {"items": {"example": item}})

    def test_public_validator_calls_each_module_once_and_deduplicates(self):
        finding = {"type": "duplicate_box", "target": "example"}
        overlap = {"type": "thing_overlap", "target": "example"}
        with patch.object(validate, "find_duplicate_boxes", return_value=[finding, finding]) as duplicates:
            with patch.object(validate, "find_thing_overlaps", return_value=[overlap]) as overlaps:
                errors, _ = validate.validate(validate.Delivery(self.delivery), False)
        duplicates.assert_called_once_with(self.delivery.resolve())
        overlaps.assert_called_once_with(self.delivery.resolve())
        self.assertEqual(errors, [finding, overlap])

    def test_shifted_identical_boxes_and_area_shortage_reach_cli(self):
        self.label("0 .5 .5 .5 .5\n0 .55 .55 .5 .5\n")
        self.panoptic["annotations"][0]["segments_info"][0]["area"] = 410
        self.json("panoptic.json", self.panoptic)
        self.manifest()
        output = self.delivery / "output.json"
        subprocess.run([sys.executable, str(ROOT / "validator/validate.py"), str(self.delivery),
                        "--out", str(output)], check=True, capture_output=True)
        errors = json.loads(output.read_text())["errors"]
        self.assertEqual(errors, [{"type": "duplicate_box", "target": "example"},
                                  {"type": "thing_overlap", "target": "example"}])

    def test_natural_overlap_with_different_box_sizes_is_clean(self):
        self.label("0 .5 .5 .5 .5\n0 .5 .5 .65 .65\n")
        self.assertEqual(find_duplicate_boxes(self.delivery), [])
        self.assertEqual(find_thing_overlaps(self.delivery), [])

    def test_crowd_and_stuff_area_differences_are_ignored(self):
        segment = self.panoptic["annotations"][0]["segments_info"][0]
        segment.update(area=900, iscrowd=1)
        self.json("panoptic.json", self.panoptic)
        self.assertEqual(find_thing_overlaps(self.delivery), [])
        segment["iscrowd"] = 0
        self.panoptic["categories"][0]["isthing"] = 0
        self.json("panoptic.json", self.panoptic)
        self.assertEqual(find_thing_overlaps(self.delivery), [])


if __name__ == "__main__":
    unittest.main()
