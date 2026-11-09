import tempfile
import unittest
from pathlib import Path

from reconcile_kpis import calculate, load_rows, reconcile


class ReconciliationTests(unittest.TestCase):
    def test_kpis_are_calculated_from_published_clean_data(self):
        rows = load_rows(Path(__file__).resolve().parents[1] / "BI_Validation_Clean.csv")
        metrics = calculate(rows)
        self.assertEqual(8000.0, metrics["Total Records"])
        self.assertAlmostEqual(86.03, metrics["SLA Achievement %"], places=2)
        self.assertAlmostEqual(4.05, metrics["Average CSAT"], places=2)

    def test_powerbi_export_is_compared_with_tolerance(self):
        metrics = {"SLA Achievement %": 86.03}
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "powerbi.csv"
            export.write_text("Metric,PowerBI_Value\nSLA Achievement %,86.03\n", encoding="utf-8")
            result = reconcile(metrics, export)
        self.assertEqual("PASS", result[0]["Status"])

    def test_missing_powerbi_metric_is_not_reported_as_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "powerbi.csv"
            export.write_text("Metric,PowerBI_Value\\n", encoding="utf-8")
            result = reconcile({"Average CSAT": 4.05}, export)
        self.assertEqual("MISSING", result[0]["Status"])


if __name__ == "__main__":
    unittest.main()
