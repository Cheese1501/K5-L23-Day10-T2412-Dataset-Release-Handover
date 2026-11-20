import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validator"))
sys.path.insert(0, str(ROOT / "scripts"))

import crosscheck
import pngutil


class CrosscheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.delivery = Path(self.tmp.name)

        for folder in ("images", "labels", "masks"):
            (self.delivery / folder).mkdir()

        (self.delivery / "classes.txt").write_text(
            "0 car\n1 truck\n", encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def make_delivery(self, label_rows, segment_rows, crowd=False):
        width = height = 40
        pixels = bytearray(width * height * 3)

        segments_info = []
        for sid, category_id, x1, y1, x2, y2 in segment_rows:
            count = 0
            for y in range(y1, y2):
                for x in range(x1, x2):
                    offset = (y * width + x) * 3
                    pixels[offset:offset + 3] = bytes(pngutil.segment_rgb(sid))
                    count += 1
            segments_info.append({
                "id": sid,
                "category_id": category_id,
                "area": count,
                "bbox": [x1, y1, x2 - x1, y2 - y1],
                "iscrowd": int(crowd),
            })

        pngutil.write_rgb(
            self.delivery / "masks" / "sample.png",
            width, height, bytes(pixels)
        )

        (self.delivery / "labels" / "sample.txt").write_text(
            "\n".join(label_rows) + ("\n" if label_rows else ""),
            encoding="utf-8",
        )

        (self.delivery / "manifest.json").write_text(
            json.dumps({
                "items": {
                    "sample": {
                        "image": "images/sample.jpg",
                        "label": "labels/sample.txt",
                        "mask": "masks/sample.png",
                    }
                }
            }),
            encoding="utf-8",
        )

        (self.delivery / "panoptic.json").write_text(
            json.dumps({
                "categories": [
                    {"id": 3, "name": "car", "isthing": 1},
                    {"id": 8, "name": "truck", "isthing": 1},
                ],
                "images": [{
                    "id": 1,
                    "file_name": "sample.jpg",
                    "width": width,
                    "height": height,
                }],
                "annotations": [{
                    "image_id": 1,
                    "file_name": "sample.png",
                    "segments_info": segments_info,
                }],
            }),
            encoding="utf-8",
        )

    def kinds(self):
        result = crosscheck.crosscheck(
            self.delivery,
            {"min_segment_pixels": 10},
        )
        return [row["possible_types"] for row in result["candidates"]]

    def test_correct_match_has_no_candidate(self):
        self.make_delivery(
            ["0 0.375 0.375 0.25 0.25"],
            [(100, 3, 10, 10, 20, 20)],
        )
        self.assertEqual(self.kinds(), [])

    def test_class_disagreement_is_ambiguous(self):
        self.make_delivery(
            ["1 0.375 0.375 0.25 0.25"],
            [(100, 3, 10, 10, 20, 20)],
        )
        self.assertIn(["class_swap", "category_swap"], self.kinds())

    def test_missing_box(self):
        self.make_delivery(
            [],
            [(100, 3, 10, 10, 20, 20)],
        )
        self.assertIn(["missing_box"], self.kinds())

    def test_bbox_drift(self):
        self.make_delivery(
            ["0 0.4375 0.375 0.125 0.25"],
            [(100, 3, 10, 10, 20, 20)],
        )
        self.assertIn(["bbox_drift"], self.kinds())

    def test_crowd_is_skipped(self):
        self.make_delivery(
            [],
            [(100, 3, 10, 10, 20, 20)],
            crowd=True,
        )
        self.assertEqual(self.kinds(), [])

    def test_instance_merge_signal(self):
        # One segment occupies two separate detection boxes.
        self.make_delivery(
            [
                "0 0.3125 0.375 0.125 0.25",
                "0 0.5625 0.375 0.125 0.25",
            ],
            [(100, 3, 8, 10, 25, 20)],
        )
        self.assertIn(["instance_merge"], self.kinds())


    def test_non_finite_detection_coordinates_are_rejected(self):
        label = self.delivery / "labels" / "bad.txt"
        label.write_text(
            "0 nan 0.5 0.4 0.4\\n"
            "0 0.5 inf 0.4 0.4\\n"
            "0 0.5 0.5 0.4 -inf\\n",
            encoding="utf-8",
        )

        boxes = crosscheck.load_boxes(
            label, {0: "car"}, width=40, height=40
        )
        self.assertEqual(boxes, [])

    def test_manifest_label_path_cannot_escape_delivery(self):
        self.make_delivery(
            ["0 0.375 0.375 0.25 0.25"],
            [(100, 3, 10, 10, 20, 20)],
        )

        manifest_path = self.delivery / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["items"]["sample"]["label"] = "../outside.txt"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaises(ValueError):
            crosscheck.crosscheck(
                self.delivery, {"min_segment_pixels": 10}
            )

    def test_instance_merge_does_not_also_emit_bbox_drift(self):
        self.make_delivery(
            [
                "0 0.3125 0.375 0.125 0.25",
                "0 0.5625 0.375 0.125 0.25",
            ],
            [(100, 3, 8, 10, 25, 20)],
        )

        result = crosscheck.crosscheck(
            self.delivery, {"min_segment_pixels": 10}
        )
        types = [
            candidate["type"]
            for candidate in result["candidates"]
        ]

        self.assertIn("instance_merge", types)
        self.assertNotIn("bbox_drift", types)


if __name__ == "__main__":
    unittest.main()
