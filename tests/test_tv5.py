"""TV5 unit tests for reviews, baseline, llm, evaluate, review_kpi, viz_reviews, and run_tv5."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import baseline, evaluate, llm, review_kpi, reviews, viz_reviews

TAXONOMY = ['location', 'cleanliness', 'host', 'value', 'amenities', 'noise', 'safety', 'check-in']


class ReviewCollectionAndPreprocessingTests(unittest.TestCase):
    def test_collect_dedupes_preserves_long_ids_and_tracks_collisions(self):
        existing = {}
        long_id = '1503006261195439072'
        snap1_rows = [
            {'id': long_id, 'listing_id': '623730253258020184', 'date': '2025-09-04', 'comments': 'Initial text'},
            {'id': long_id, 'listing_id': '623730253258020184', 'date': '2025-09-04', 'comments': 'Initial text'},
            {'id': 'bad-id', 'listing_id': '10', 'date': '2025-09-04', 'comments': 'Valid comment'},
            {'id': '101', 'listing_id': '10', 'date': 'bad-date', 'comments': 'Valid comment'},
            {'id': '102', 'listing_id': '10', 'date': '2025-09-04', 'comments': '<br/>   '},
        ]
        issues1 = reviews.collect(snap1_rows, '2025-09-11', existing)
        self.assertEqual(issues1['duplicate_review_in_snapshot'], 1)
        self.assertEqual(issues1['invalid_review_id'], 1)
        self.assertEqual(issues1['invalid_review_date'], 1)
        self.assertEqual(issues1['empty_review_comment'], 1)
        self.assertIn(long_id, existing)
        self.assertEqual(existing[long_id]['first_seen_snapshot'], '2025-09-11')

        # Mốc sau có cùng review_id nhưng nội dung thay đổi -> báo review_text_collision và cập nhật text mới nhất
        snap2_rows = [
            {'id': long_id, 'listing_id': '623730253258020184', 'date': '2025-09-04', 'comments': 'Updated 2026-06-15 text'},
        ]
        issues2 = reviews.collect(snap2_rows, '2026-06-15', existing)
        self.assertEqual(issues2['duplicate_review_across_snapshots'], 1)
        self.assertEqual(issues2['review_text_collision'], 1)
        self.assertEqual(existing[long_id]['comments'], 'Updated 2026-06-15 text')
        self.assertEqual(existing[long_id]['first_seen_snapshot'], '2025-09-11')

    def test_preprocessing_helpers(self):
        cleaned = reviews.clean_comment('Great stay!<br/>Very   clean &amp; quiet.')
        self.assertEqual(cleaned, 'Great stay! Very clean & quiet.')
        self.assertEqual(reviews.detect_language_simple('Bel endroit tranquille, bien situé'), 'fr')
        self.assertEqual(reviews.detect_language_simple('Die Wohnung liegt in einer ruhigen Nachbarschaft'), 'de')
        self.assertEqual(reviews.detect_language_simple('Great place and very clean room'), 'en')
        aspects = reviews.extract_aspect_keywords('Walk to subway station, spotless bathroom and friendly host', TAXONOMY)
        self.assertEqual(set(aspects), {'location', 'cleanliness', 'host', 'amenities'})


class BaselineTests(unittest.TestCase):
    def test_baseline_classifies_positive_mixed_and_negative(self):
        pos = baseline.predict({
            'review_id': '1001',
            'comments': 'Fantastic stay, spotless apartment and very responsive host!',
        })
        self.assertEqual(pos, {'review_id': '1001', 'sentiment': 'positive', 'source': 'keyword_baseline'})

        mixed = baseline.predict({
            'review_id': '1002',
            'comments': 'Everything was good except there was stain on the sheets and the sink drips.',
        })
        self.assertEqual(mixed['sentiment'], 'mixed')

        neg = baseline.predict({
            'review_id': '1003',
            'comments': 'It is a "ok" house but too old and lack of maintenance, hair in the bathroom and slippery stairs.',
        })
        self.assertEqual(neg['sentiment'], 'negative')

        resolved = baseline.predict({
            'review_id': '1004',
            'comments': 'Very responsive hosts even when there was a small problem with check in they helped us immediately and it didn’t even feel like a problem. Clean room and perfect location.',
        })
        self.assertEqual(resolved['sentiment'], 'positive')


class LlmValidationAndCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cfg = {
            'seed': 42,
            'llm': {
                'model': 'gemini-3.5-flash-lite',
                'sample_size': 10,
                'aspects': TAXONOMY,
                'cache': 'data/processed/llm_cache.jsonl',
                'retries': 2,
            },
        }
        self.reviews = [
            {'review_id': '2001', 'listing_id': '10', 'date': '2025-08-01', 'comments': 'Clean room, great location.'},
            {'review_id': '2002', 'listing_id': '20', 'date': '2025-08-02', 'comments': 'Nice host but noisy street.'},
        ]

    def test_validate_accepts_valid_and_rejects_bad_schema_or_taxonomy(self):
        valid = llm.validate(
            {
                'sentiment': 'mixed',
                'language': 'EN',
                'positive_aspects': ['host', 'host'],
                'negative_aspects': ['noise'],
            },
            TAXONOMY,
        )
        self.assertEqual(valid['sentiment'], 'mixed')
        self.assertEqual(valid['language'], 'en')
        self.assertEqual(valid['positive_aspects'], ['host'])
        self.assertEqual(valid['negative_aspects'], ['noise'])

        bad_cases = [
            {'sentiment': 'neutral', 'language': 'en', 'positive_aspects': [], 'negative_aspects': []},
            {'sentiment': 'positive', 'language': '', 'positive_aspects': [], 'negative_aspects': []},
            {'sentiment': 'positive', 'language': 'en', 'positive_aspects': ['breakfast'], 'negative_aspects': []},
            {'sentiment': 'positive', 'language': 'en', 'positive_aspects': 'location', 'negative_aspects': []},
        ]
        for bad in bad_cases:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                llm.validate(bad, TAXONOMY)

    def test_analyze_uses_cache_and_invalidates_on_text_model_or_taxonomy_change(self):
        responses = [
            '```json\n{"sentiment": "positive", "language": "en", "positive_aspects": ["cleanliness", "location"], "negative_aspects": []}\n```',
            '{"sentiment": "mixed", "language": "en", "positive_aspects": ["host"], "negative_aspects": ["noise"]}',
        ]
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'fake-key'}), patch.object(
            llm, 'call_gemini_api', side_effect=responses
        ) as api_mock:
            out1 = llm.analyze(self.reviews, self.cfg, self.root, {'2001', '2002'}, allow_api=True)
            self.assertEqual(len(out1), 2)
            self.assertEqual(api_mock.call_count, 2)

            # Lần chạy thứ 2 với cùng input phải lấy từ cache 100% (không gọi API)
            out2 = llm.analyze(self.reviews, self.cfg, self.root, {'2001', '2002'})
            self.assertEqual(out2, out1)
            self.assertEqual(api_mock.call_count, 2)

        # Nếu đổi nội dung comment của 2001 thì không được dùng cache cũ
        changed_reviews = [
            {**self.reviews[0], 'comments': 'Dirty bathroom and rude host.'},
            self.reviews[1],
        ]
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'fake-key'}), patch.object(
            llm,
            'call_gemini_api',
            return_value='{"sentiment": "negative", "language": "en", "positive_aspects": [], "negative_aspects": ["cleanliness", "host"]}',
        ) as api_mock2:
            out3 = llm.analyze(changed_reviews, self.cfg, self.root, {'2001', '2002'}, allow_api=True)
            self.assertEqual(api_mock2.call_count, 1)
            self.assertEqual(out3[0]['sentiment'], 'negative')

    def test_analyze_retries_and_never_turns_api_failure_into_default_label(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'fake-key'}), patch.object(
            llm, 'call_gemini_api', side_effect=TimeoutError('API timed out')
        ), patch('time.sleep'):
            with self.assertRaises(RuntimeError):
                llm.analyze(self.reviews[:1], self.cfg, self.root, {'2001'}, allow_api=True)


class EvaluationAndKpiTests(unittest.TestCase):
    def test_evaluate_computes_macro_f1_and_rejects_missing_or_duplicate_ids(self):
        labels = [
            {'review_id': '1', 'sentiment': 'positive'},
            {'review_id': '2', 'sentiment': 'mixed'},
            {'review_id': '3', 'sentiment': 'negative'},
        ]
        preds = [
            {'review_id': '1', 'sentiment': 'positive'},
            {'review_id': '2', 'sentiment': 'mixed'},
            {'review_id': '3', 'sentiment': 'negative'},
        ]
        res = evaluate.evaluate(preds, labels, 'llm')[0]
        self.assertEqual(res['paired_n'], 3)
        self.assertEqual(res['manual_n'], 3)
        self.assertEqual(res['accuracy'], 1.0)
        self.assertEqual(res['macro_f1'], 1.0)
        self.assertFalse(res['meets_100_paired'])

        # Thiếu dự đoán cho review_id '3' -> phải báo lỗi ValueError
        with self.assertRaisesRegex(ValueError, 'Missing predictions'):
            evaluate.evaluate(preds[:2], labels, 'llm')

        # Nhãn trùng review_id -> phải báo lỗi ValueError
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            evaluate.evaluate(preds, labels + [labels[0]], 'llm')

    def test_guest_kpi_does_not_multiply_reviews_across_snapshots(self):
        preds = [
            {
                'review_id': '10',
                'listing_id': '500',
                'sentiment': 'positive',
                'positive_aspects': ['location', 'cleanliness'],
                'negative_aspects': [],
                'source': 'gemini-3.5-flash-lite',
            },
            {
                'review_id': '11',
                'listing_id': '500',
                'sentiment': 'mixed',
                'positive_aspects': ['location'],
                'negative_aspects': ['noise'],
                'source': 'gemini-3.5-flash-lite',
            },
        ]
        # Cùng listing 500 xuất hiện ở 4 mốc snapshot
        listings = [
            {'snapshot_date': snap, 'listing_id': '500', 'analysis_area': 'Downtown'}
            for snap in ['2025-09-11', '2025-12-12', '2026-03-19', '2026-06-15']
        ]
        kpis = {row['metric']: row for row in review_kpi.guest_kpi(preds, listings, {'llm': {'aspects': TAXONOMY}})}
        self.assertEqual(kpis['guest_issue_rate']['value'], 0.5)
        self.assertEqual(kpis['guest_issue_rate']['sample_n'], 2)
        self.assertEqual(kpis['area_guest_issue_rate']['sample_n'], 2)
        self.assertEqual(kpis['area_guest_issue_rate']['value'], 0.5)


class VisualizationAndRunnerTests(unittest.TestCase):
    def test_viz_reviews_creates_valid_svg_files_with_scope_and_n(self):
        tables = {
            'reviews': [
                {'review_id': '1', 'date': '2025-06-10', 'comments': 'Clean and great host'},
                {'review_id': '2', 'date': '2025-08-15', 'comments': 'Good location but noisy'},
            ],
            'llm_reviews': [
                {
                    'review_id': '1',
                    'sentiment': 'positive',
                    'language': 'en',
                    'positive_aspects': ['cleanliness', 'host'],
                    'negative_aspects': [],
                    'source': 'gemini-3.5-flash-lite',
                },
                {
                    'review_id': '2',
                    'sentiment': 'mixed',
                    'language': 'en',
                    'positive_aspects': ['location'],
                    'negative_aspects': ['noise'],
                    'source': 'gemini-3.5-flash-lite',
                },
            ],
            'evaluation': [
                {'source': 'llm', 'paired_n': 2, 'manual_n': 2, 'accuracy': 1.0, 'macro_f1': 1.0, 'meets_100_paired': False},
                {'source': 'baseline', 'paired_n': 2, 'manual_n': 2, 'accuracy': 0.5, 'macro_f1': 0.3333, 'meets_100_paired': False},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            paths = viz_reviews.render(tables, Path(tmp), {'city': 'Toronto', 'llm': {'aspects': TAXONOMY}})
            self.assertEqual(len(paths), 4)
            for p in paths:
                self.assertTrue(p.exists())
                self.assertGreater(p.stat().st_size, 200)
                root = ET.parse(p).getroot()
                self.assertIn('n =', ''.join(root.itertext()))

    def test_run_tv5_cli_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'configs').mkdir()
            cfg = json.loads((ROOT / 'configs/toronto.yaml').read_text(encoding='utf-8'))
            config_path = root / 'configs/toronto.yaml'
            config_path.write_text(json.dumps(cfg), encoding='utf-8')
            shutil.copytree(ROOT / 'data/samples/demo', root / 'data/samples/demo')
            shutil.copy(ROOT / 'data/samples/demo_labels.csv', root / 'data/samples/demo_labels.csv')

            res = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/run_tv5.py'), '--config', str(config_path), '--demo'],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertTrue((root / 'data/processed/demo/tv5/kpi_guest.csv').exists())
            self.assertEqual(len(list((root / 'figures/demo/tv5').glob('*.svg'))), 4)


if __name__ == '__main__':
    unittest.main()
