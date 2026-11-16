"""Test calendar.aggregate, calendar.metrics và viz_calendar.render (TV4)."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from airbnb import my_calendar, viz_calendar


LARGE_ID = "1502977270045215452"
SNAP = "2025-09-11"


class CalendarAggregateTests(unittest.TestCase):
    def test_streaming_window_dedupe_and_long_id(self):
        # Truyền iterator để đảm bảo aggregate đọc streaming 1 lần và giữ nguyên ID 19 chữ số
        records = iter([
            {"listing_id": LARGE_ID, "date": "2025-09-10", "available": "t"},  # trước snapshot -> bỏ qua
            {"listing_id": LARGE_ID, "date": "2025-09-11", "available": "t"},  # ngày 1 (hợp lệ)
            {"listing_id": LARGE_ID, "date": "2025-09-11", "available": "f"},  # trùng khóa -> bỏ qua
            {"listing_id": LARGE_ID, "date": "2025-09-12", "available": "f"},  # ngày 2 (hợp lệ)
            {"listing_id": LARGE_ID, "date": "2025-10-10", "available": "t"},  # ngày thứ 30 (hợp lệ với window=30)
            {"listing_id": LARGE_ID, "date": "2025-10-11", "available": "t"},  # ngày thứ 31 (ngoài window=30)
        ])

        summary, issues = my_calendar.aggregate(records, SNAP, window_days=30, listing_ids={LARGE_ID})

        self.assertEqual(len(summary), 1)
        row = summary[0]
        self.assertEqual(row["snapshot_date"], SNAP)
        self.assertEqual(row["listing_id"], LARGE_ID)
        self.assertEqual(row["available_days"], 2)
        self.assertEqual(row["observed_days"], 3)
        self.assertEqual(row["expected_days"], 30)
        self.assertAlmostEqual(row["availability_rate"], round(2 / 3, 6))
        self.assertEqual(issues, {"duplicate_calendar": 1})

    def test_window_90_vs_30_days(self):
        records = [
            {"listing_id": "10", "date": "2025-09-15", "available": "t"},  # nằm trong cả 30 và 90 ngày
            {"listing_id": "10", "date": "2025-11-01", "available": "f"},  # ngày thứ 51 -> chỉ nằm trong 90 ngày
            {"listing_id": "10", "date": "2025-12-10", "available": "t"},  # ngày thứ 90 -> nằm ngoài [start, start+90)
        ]

        sum_30, _ = my_calendar.aggregate(records, SNAP, window_days=30, listing_ids={"10"})
        sum_90, _ = my_calendar.aggregate(records, SNAP, window_days=90, listing_ids={"10"})

        self.assertEqual(sum_30[0]["observed_days"], 1)
        self.assertEqual(sum_30[0]["available_days"], 1)
        self.assertEqual(sum_30[0]["expected_days"], 30)

        self.assertEqual(sum_90[0]["observed_days"], 2)
        self.assertEqual(sum_90[0]["available_days"], 1)
        self.assertEqual(sum_90[0]["expected_days"], 90)
        self.assertAlmostEqual(sum_90[0]["availability_rate"], 0.5)

    def test_issue_counters_for_invalid_and_orphan_rows(self):
        records = [
            {"listing_id": "1", "date": "not-a-date", "available": "t"},      # invalid_calendar_date
            {"listing_id": "999", "date": "2025-09-12", "available": "t"},     # orphan_calendar (ngoài cohort 1.000 ID)
            {"listing_id": "1", "date": "2025-09-12", "available": "maybe"},   # invalid_available
            {"listing_id": "1", "date": "2025-09-13", "available": "T"},       # hợp lệ (không phân biệt hoa/thường)
        ]

        summary, issues = my_calendar.aggregate(records, SNAP, window_days=90, listing_ids={"1"})

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["available_days"], 1)
        self.assertEqual(summary[0]["observed_days"], 1)
        self.assertEqual(
            issues,
            {
                "invalid_calendar_date": 1,
                "orphan_calendar": 1,
                "invalid_available": 1,
            },
        )


class CalendarMetricsAndBreakdownTests(unittest.TestCase):
    def test_metrics_aggregates_weighted_rate_by_analysis_area(self):
        cal_rows = [
            {
                "snapshot_date": SNAP,
                "listing_id": "1",
                "available_days": 30,
                "observed_days": 90,
                "expected_days": 90,
                "availability_rate": round(30 / 90, 6),
            },
            {
                "snapshot_date": SNAP,
                "listing_id": "2",
                "available_days": 60,
                "observed_days": 90,
                "expected_days": 90,
                "availability_rate": round(60 / 90, 6),
            },
            {
                "snapshot_date": SNAP,
                "listing_id": "3",
                "available_days": 45,
                "observed_days": 45,
                "expected_days": 90,
                "availability_rate": 1.0,
            },
        ]
        listings = [
            {"snapshot_date": SNAP, "listing_id": "1", "analysis_area": "A01"},
            {"snapshot_date": SNAP, "listing_id": "2", "analysis_area": "A01"},
            {"snapshot_date": SNAP, "listing_id": "3", "analysis_area": "A02"},
        ]

        kpi = my_calendar.metrics(cal_rows, listings, cfg={})
        self.assertEqual(len(kpi), 2)

        by_area = {r["analysis_area"]: r for r in kpi}
        self.assertEqual(by_area["A01"]["listing_n"], 2)
        self.assertEqual(by_area["A01"]["observed_days"], 180)
        self.assertEqual(by_area["A01"]["expected_days"], 180)
        self.assertAlmostEqual(by_area["A01"]["availability_rate"], 0.5)

        self.assertEqual(by_area["A02"]["listing_n"], 1)
        self.assertEqual(by_area["A02"]["observed_days"], 45)
        self.assertEqual(by_area["A02"]["expected_days"], 90)
        self.assertAlmostEqual(by_area["A02"]["availability_rate"], 1.0)

    def test_weekday_vs_weekend_breakdown(self):
        # 2025-09-11 là Thứ Năm (weekday); 2025-09-12..14 là T6-CN (weekend)
        records = [
            {"listing_id": "1", "date": "2025-09-11", "available": "f"},  # Thu -> weekday
            {"listing_id": "1", "date": "2025-09-12", "available": "t"},  # Fri -> weekend
            {"listing_id": "1", "date": "2025-09-13", "available": "t"},  # Sat -> weekend
            {"listing_id": "1", "date": "2025-09-14", "available": "f"},  # Sun -> weekend
        ]
        rows = my_calendar.weekday_weekend_breakdown(records, SNAP, window_days=7, listing_ids={"1"})
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["weekday_availability_rate"], 0.0)
        self.assertAlmostEqual(rows[0]["weekend_availability_rate"], round(2 / 3, 6))
        self.assertAlmostEqual(rows[0]["weekend_minus_weekday"], round(2 / 3, 6))


class VizCalendarTests(unittest.TestCase):
    def test_render_creates_valid_png_files_and_rejects_invalid_rate(self):
        tables = {
            "calendar_kpi": [
                {
                    "snapshot_date": "2025-09-11",
                    "analysis_area": "A01",
                    "availability_rate": 0.45,
                    "observed_days": 90,
                    "expected_days": 90,
                    "listing_n": 1,
                },
                {
                    "snapshot_date": "2026-06-15",
                    "analysis_area": "A01",
                    "availability_rate": 0.60,
                    "observed_days": 90,
                    "expected_days": 90,
                    "listing_n": 1,
                },
            ],
            "calendar": [
                {
                    "snapshot_date": "2026-06-15",
                    "listing_id": "1",
                    "available_days": 54,
                    "observed_days": 90,
                    "expected_days": 90,
                    "availability_rate": 0.60,
                }
            ],
            "listings": [
                {
                    "snapshot_date": "2026-06-15",
                    "listing_id": "1",
                    "analysis_area": "A01",
                    "price": 180.0,
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "figures"
            paths = viz_calendar.render(tables, out_dir, cfg={})
            self.assertEqual(len(paths), 3)
            for p in paths:
                self.assertTrue(p.exists())
                # Kiểm tra magic bytes chuẩn của file PNG
                self.assertTrue(p.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

        bad_tables = {
            "calendar_kpi": [
                {
                    "snapshot_date": "2026-06-15",
                    "analysis_area": "A01",
                    "availability_rate": 1.25,  # > 1.0 -> phải báo lỗi
                    "observed_days": 90,
                    "expected_days": 90,
                    "listing_n": 1,
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                viz_calendar.render(bad_tables, Path(tmp), cfg={})


if __name__ == "__main__":
    unittest.main()