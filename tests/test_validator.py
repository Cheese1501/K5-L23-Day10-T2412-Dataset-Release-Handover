import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validator"))

import validate as validator


class DetectionValidationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.label = Path(self.tmp.name) / "sample.txt"
        self.classes = {0: "car", 1: "truck"}

    def tearDown(self):
        self.tmp.cleanup()

    def check_row(self, row):
        self.label.write_text(row + "\n", encoding="utf-8")
        return validator.detection(self.label, self.classes, 100, 100)

    def test_valid_box_is_accepted(self):
        boxes, errors = self.check_row("0 0.5 0.5 0.4 0.4")
        self.assertEqual(len(boxes), 1)
        self.assertEqual(errors, set())
        self.assertEqual(boxes[0].name, "car")

    def test_non_numeric_class_is_invalid_class(self):
        boxes, errors = self.check_row("abc 0.5 0.5 0.4 0.4")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"invalid_class"})

    def test_out_of_range_class_is_invalid_class(self):
        boxes, errors = self.check_row("80")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"invalid_class"})

    def test_valid_class_without_geometry_is_bbox_error(self):
        boxes, errors = self.check_row("0 0.5")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"bbox_out_of_bounds"})

    def test_non_numeric_geometry_is_bbox_error(self):
        boxes, errors = self.check_row("0 0.5 nope 0.4 0.4")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"bbox_out_of_bounds"})

    def test_out_of_bounds_box_is_rejected(self):
        boxes, errors = self.check_row("0 0.99 0.5 0.4 0.4")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"bbox_out_of_bounds"})

    def test_non_finite_class_is_invalid_class(self):
        boxes, errors = self.check_row("nan 0.5 0.5 0.4 0.4")
        self.assertEqual(boxes, [])
        self.assertEqual(errors, {"invalid_class"})


class DeliveryStructureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, name, value):
        (self.root / name).write_text(
            json.dumps(value), encoding="utf-8"
        )

    def test_manifest_requires_items_object(self):
        self.write_json("manifest.json", {})
        with self.assertRaisesRegex(ValueError, "manifest.json"):
            validator.Delivery(self.root)

    def test_metadata_rejects_duplicate_image(self):
        self.write_json("manifest.json", {"items": {}})
        self.write_json("metadata.json", {
            "items": [
                {"image": "sample"},
                {"image": "sample"},
            ]
        })
        with self.assertRaisesRegex(ValueError, "image trùng"):
            validator.Delivery(self.root)


if __name__ == "__main__":
    unittest.main()


class FullValidationIntegrationTest(unittest.TestCase):
    def setUp(self):
        import hashlib

        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        for folder in ("images", "labels", "masks"):
            (self.root / folder).mkdir()

        self.hash_bytes = lambda data: hashlib.sha256(data).hexdigest()

        # Hai mask 20x20:
        # segment 1: 100 pixel (10x10), category car.
        # segment 2: 25 pixel (5x5), cố ý dùng category ID không tồn tại.
        self.make_mask("sample_a", include_invalid_segment=True)
        self.make_mask("sample_b", include_invalid_segment=False)

        # Ảnh A khớp chính xác; ảnh B cố ý lệch box để tạo bbox_drift.
        label_a = b"0 0.35 0.35 0.5 0.5\n"
        label_b = b"0 0.45 0.35 0.5 0.5\n"
        (self.root / "labels/sample_a.txt").write_bytes(label_a)
        (self.root / "labels/sample_b.txt").write_bytes(label_b)

        # sample_a cố ý thiếu ảnh.
        image_b = b"synthetic-jpeg-b"
        (self.root / "images/sample_b.jpg").write_bytes(image_b)

        mask_a = (self.root / "masks/sample_a.png").read_bytes()
        mask_b = (self.root / "masks/sample_b.png").read_bytes()

        self.write_json("manifest.json", {
            "dataset": "synthetic-test",
            "num_classes": 2,
            "items": {
                "sample_a": {
                    "image": "images/sample_a.jpg",
                    "label": "labels/sample_a.txt",
                    "mask": "masks/sample_a.png",
                    "image_sha256": self.hash_bytes(b"expected-but-missing"),
                    "label_sha256": "0" * 64,
                    "mask_sha256": self.hash_bytes(mask_a),
                },
                "sample_b": {
                    "image": "images/sample_b.jpg",
                    "label": "labels/sample_b.txt",
                    "mask": "masks/sample_b.png",
                    "image_sha256": self.hash_bytes(image_b),
                    "label_sha256": self.hash_bytes(label_b),
                    "mask_sha256": self.hash_bytes(mask_b),
                },
            },
        })

        self.write_json("metadata.json", {
            "items": [
                {
                    "image": "sample_a",
                    "scene_id": "shared_scene",
                    "split": "train",
                    "job_id": "job_a",
                    "guideline_version": "v1.3",
                },
                {
                    "image": "sample_b",
                    "scene_id": "shared_scene",
                    "split": "val",
                    "job_id": "job_b",
                    "guideline_version": "v1.3",
                },
            ],
        })

        (self.root / "jobs.csv").write_text(
            "job_id,annotator,reviewer,guideline\n"
            "job_a,ann_a,rev_a,v1.2\n"
            "job_b,ann_b,rev_b,v1.3\n",
            encoding="utf-8",
        )

        (self.root / "classes.txt").write_text(
            "0 car\n1 truck\n",
            encoding="utf-8",
        )

        categories = [
            {"id": 3, "name": "car", "isthing": 1},
            {"id": 8, "name": "truck", "isthing": 1},
        ]

        annotations = [
            {
                "image_id": 1,
                "file_name": "sample_a.png",
                "segments_info": [
                    {
                        "id": 1,
                        "category_id": 3,
                        "area": 101,
                        "bbox": [2, 2, 10, 10],
                        "iscrowd": 0,
                    },
                    {
                        "id": 2,
                        "category_id": 999,
                        "area": 25,
                        "bbox": [14, 14, 5, 5],
                        "iscrowd": 0,
                    },
                ],
            },
            {
                "image_id": 2,
                "file_name": "sample_b.png",
                "segments_info": [
                    {
                        "id": 1,
                        "category_id": 3,
                        "area": 100,
                        "bbox": [2, 2, 10, 10],
                        "iscrowd": 0,
                    },
                ],
            },
        ]

        self.write_json("panoptic.json", {
            "categories": categories,
            "images": [
                {
                    "id": 1,
                    "file_name": "sample_a.jpg",
                    "width": 20,
                    "height": 20,
                },
                {
                    "id": 2,
                    "file_name": "sample_b.jpg",
                    "width": 20,
                    "height": 20,
                },
            ],
            "annotations": annotations,
        })

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, name, value):
        (self.root / name).write_text(
            json.dumps(value), encoding="utf-8"
        )

    def make_mask(self, stem, include_invalid_segment):
        width = height = 20
        pixels = bytearray(width * height * 3)

        for y in range(2, 12):
            for x in range(2, 12):
                offset = (y * width + x) * 3
                pixels[offset:offset + 3] = bytes(validator.pngutil.segment_rgb(1))

        if include_invalid_segment:
            for y in range(14, 19):
                for x in range(14, 19):
                    offset = (y * width + x) * 3
                    pixels[offset:offset + 3] = bytes(validator.pngutil.segment_rgb(2))

        validator.pngutil.write_rgb(
            self.root / "masks" / f"{stem}.png",
            width,
            height,
            bytes(pixels),
        )

    def test_rule_errors_are_detected(self):
        delivery = validator.Delivery(self.root)
        errors, candidates = validator.validate(delivery, candidates=True)

        actual = {(row["type"], row["target"]) for row in errors}
        expected = {
            ("missing_image", "sample_a"),
            ("wrong_hash", "sample_a"),
            ("guideline_mismatch", "sample_a"),
            ("invalid_category_id", "sample_a"),
            ("thing_overlap", "sample_a"),
            ("scene_leak", "shared_scene"),
        }

        self.assertEqual(actual, expected)
        self.assertIsInstance(candidates, list)

    def test_candidate_schema_is_compatible_with_review_tool(self):
        delivery = validator.Delivery(self.root)
        _, candidates = validator.validate(delivery, candidates=True)

        self.assertTrue(candidates, "Fixture phải tạo ít nhất một candidate")
        self.assertTrue(
            any("bbox_drift" in row["possible_types"] for row in candidates),
            "Fixture ảnh B phải tạo candidate bbox_drift",
        )

        for candidate in candidates:
            self.assertIn("image", candidate)
            self.assertIn("type", candidate)
            self.assertIn("possible_types", candidate)
            self.assertIn("reason", candidate)
            self.assertIn("detection", candidate)
            self.assertIn("panoptic", candidate)


if __name__ == "__main__":
    unittest.main()
