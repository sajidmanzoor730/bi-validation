"""Regression tests for the BI Validation project's published data assets."""
import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_project import ROOT, validate


class ProjectValidationTests(unittest.TestCase):
    def test_published_project_passes_quality_gate(self):
        failures, metrics = validate(ROOT)
        self.assertEqual([], failures, "\n".join(failures))
        self.assertEqual(8160, metrics["raw_rows"])
        self.assertEqual(8000, metrics["clean_rows"])
        self.assertEqual(160, metrics["duplicate_raw_rows"])
        self.assertEqual(24, metrics["issue_types"])
        self.assertEqual(765, metrics["row_issue_findings"])

    def test_clean_dataset_has_sla_baseline(self):
        failures, metrics = validate(ROOT)
        self.assertEqual([], failures, "\n".join(failures))
        self.assertIsNotNone(metrics["sla_achievement_pct"])
        self.assertGreater(metrics["sla_achievement_pct"], 0)
        self.assertLessEqual(metrics["sla_achievement_pct"], 100)



    def test_quality_gate_detects_a_broken_sla_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            for filename in (
                "BI_Validation_Raw.csv",
                "BI_Validation_Clean.csv",
                "BI_Validation_Data_Quality_Issues.csv",
                "BI_Validation_Row_Issue_Log.csv",
            ):
                shutil.copy2(ROOT / filename, temp_root / filename)

            clean_path = temp_root / "BI_Validation_Clean.csv"
            with clean_path.open(newline="", encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
                fieldnames = list(rows[0])
            rows[0]["SLA_Target_Minutes"] = "999"
            with clean_path.open("w", newline="", encoding="utf-8") as target:
                writer = csv.DictWriter(target, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            failures, _ = validate(temp_root)
            self.assertTrue(any("SLA targets do not match" in failure for failure in failures))

if __name__ == "__main__":
    unittest.main()
