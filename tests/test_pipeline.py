import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from airbnb.qa import clean_listings
from airbnb.calendar import aggregate
from airbnb.llm import validate
from airbnb.evaluate import evaluate

class PipelineTests(unittest.TestCase):
    def test_four_snapshot_demo_in_clean_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)/"repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".venv", "__pycache__", "*.egg-info", "processed", "generated", "figures", ".git"))
            subprocess.run([sys.executable, str(repo/"run_pipeline.py"), "--demo", "--skip-llm"], cwd=temp, check=True, capture_output=True)
            with (repo/"data/processed/demo/kpi_market.csv").open() as f:
                rows = list(csv.DictReader(f))
            totals = [r for r in rows if r["neighbourhood"] == "ALL"]
            self.assertEqual(len(totals), 4)
            self.assertEqual([int(r["supply"]) for r in totals], [3]*4)
            self.assertTrue(all(abs(float(r["availability_rate"])-2/3)<1e-9 for r in totals))
            self.assertTrue((repo/"figures/demo/spatial.svg").exists())
            self.assertEqual((repo/"data/processed/demo/kpi_guest.csv").read_text().count("\n"), 1)
    def test_outlier_flag_keeps_row(self):
        cfg = json.loads((ROOT/"configs/toronto.yaml").read_text())
        rows, report = clean_listings([{"id":"1","price":"$999,999.00"},{"id":"1","price":"2"}], "2025-01-01", cfg)
        self.assertEqual(len(rows),1)
        self.assertIn("price_outlier", rows[0]["qa_flags"])
        self.assertEqual(next(r for r in report if r["rule"]=="duplicate_listing")["affected_rows"],1)
    def test_calendar_bounds_and_orphans(self):
        rows=[{"listing_id":"1","date":"2025-01-01","available":"t"},{"listing_id":"1","date":"2025-04-01","available":"t"},{"listing_id":"2","date":"2025-01-01","available":"f"}]
        result, issues=aggregate(rows,"2025-01-01",90,{"1"})
        self.assertEqual(result[0]["observed_days"],1)
        self.assertEqual(issues["orphan_calendar"],1)
    def test_llm_schema_and_evaluation(self):
        with self.assertRaises(ValueError):
            validate({"sentiment":"positive","language":"en","positive_aspects":["invented"],"negative_aspects":[]},["host"])
        metrics=evaluate([{"review_id":"1","sentiment":"negative"}],[{"review_id":"1","sentiment":"negative"}],"test")
        self.assertEqual(metrics[0]["accuracy"],1)
        self.assertFalse(metrics[0]["meets_100_paired"])

if __name__ == "__main__": unittest.main()
