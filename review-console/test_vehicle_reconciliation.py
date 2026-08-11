import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile

from vehicle_reconciliation import (
    build_vehicle_reconciliation,
    compact_vehicle_context,
    extract_vehicle_records,
    index_source_units,
    reconcile_vehicle_records,
)


PPT_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def slide_xml(text: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <p:sld xmlns:p="{PPT_NS}" xmlns:a="{DRAWING_NS}">
      <p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p>
      </p:txBody></p:sp></p:spTree></p:cSld>
    </p:sld>"""


class VehicleReconciliationTests(unittest.TestCase):
    def test_indexes_every_slide_and_finds_count_on_last_slide(self):
        with TemporaryDirectory() as temporary:
            deck = Path(temporary) / "large.pptx"
            with zipfile.ZipFile(deck, "w") as archive:
                for number in range(1, 135):
                    text = (
                        "Zone 22 AGV COUNT ANALYSIS Conclusion: "
                        "21 units of VNE40 are required"
                        if number == 134
                        else f"ordinary slide {number}"
                    )
                    archive.writestr(f"ppt/slides/slide{number}.xml", slide_xml(text))

            index = index_source_units(deck)
            records = extract_vehicle_records(index)

            self.assertTrue(index["complete"])
            self.assertEqual(134, index["total_units"])
            self.assertEqual(134, index["indexed_units"])
            self.assertTrue(
                any(
                    record["source"].endswith("#slide134")
                    and record["quantity"] == 21
                    for record in records
                )
            )

    def test_conclusion_and_table_total_conflict_blocks_without_override(self):
        index = {
            "file": "zone24.pptx",
            "supported": True,
            "total_units": 2,
            "indexed_units": 2,
            "complete": True,
            "units": [
                {
                    "locator": "slide1",
                    "text": "Zone 24 AGV COUNT ANALYSIS Conclusion: 5 units of VNE40 are required",
                },
                {
                    "locator": "slide2",
                    "text": "Zone 24 VNE40 table Total 6 units",
                },
            ],
        }
        records = extract_vehicle_records(index)
        result = reconcile_vehicle_records([index], records)

        self.assertEqual("BLOCKED", result["status"])
        self.assertTrue(
            any(
                conflict["type"] == "conclusion_table_mismatch"
                for conflict in result["conflicts"]
            )
        )

    def test_authoritative_override_wins_and_reports_detail_gap(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            note = root / "notes.txt"
            note.write_text(
                "Zone 1 AGV COUNT ANALYSIS 24 units of VNE40 are required",
                encoding="utf-8",
            )
            override = root / "vehicle_total_override.json"
            override.write_text(
                json.dumps(
                    {"authoritative_total": 98, "expression": "89+9"},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = build_vehicle_reconciliation([note, override])

            self.assertEqual(98, result["authoritative_total"])
            self.assertEqual("89+9", result["expression"])
            self.assertEqual("PASS_WITH_NOTE", result["status"])
            self.assertTrue(
                any(
                    conflict["type"] == "authoritative_total_detail_gap"
                    for conflict in result["conflicts"]
                )
            )

    def test_compact_context_has_hard_character_budget(self):
        result = {
            "coverage": {"complete": True, "files": []},
            "authoritative_total": 98,
            "expression": "89+9",
            "calculated_subtotal": 24,
            "conflicts": [{"type": "x", "detail": "a" * 5000}],
            "status": "PASS_WITH_NOTE",
        }

        context = compact_vehicle_context(result, max_chars=800)

        self.assertLessEqual(len(context), 800)
        self.assertIn('"authoritative_total":98', context)


if __name__ == "__main__":
    unittest.main()
