"""Regression tests for the BI Validation project's published data assets."""
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


if __name__ == "__main__":
    unittest.main()
