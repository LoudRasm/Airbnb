"""TV1-only analysis/render/runner checks; never import the other members' modules."""
import contextlib
from copy import deepcopy
import csv
import gzip
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import analysis, viz_market

SPEC = importlib.util.spec_from_file_location('tv1_runner', ROOT / 'scripts/run_tv1.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
DATES = ['2026-01-01', '2026-04-01']


def row(snapshot, identity, host='10', room='Private room'):
    return {'snapshot_date': snapshot, 'listing_id': identity, 'host_id': host, 'room_type': room}


def records():
    return [row(DATES[0], '1'), row(DATES[0], '2', '20'), row(DATES[0], '3', None),
            row(DATES[1], '1', '11'), row(DATES[1], '2', '20', 'Entire home/apt'), row(DATES[1], '4', '40')]


class CohortAnalysisTests(unittest.TestCase):
    def test_matched_changes_and_presence_conservation(self):
        result = analysis.churn(iter(records()), DATES)[0]
        self.assertEqual((result['new'], result['retained'], result['disappeared']), (1, 2, 1))
        self.assertEqual(result['previous_n'], result['retained'] + result['disappeared'])
        self.assertEqual(result['current_n'], result['retained'] + result['new'])
        self.assertAlmostEqual(result['entry_rate'], 1/3)
        self.assertAlmostEqual(result['exit_rate'], 1/3)
        self.assertEqual((result['host_comparable'], result['host_changed'], result['host_change_rate']), (2, 1, 0.5))
        self.assertEqual((result['room_type_comparable'], result['room_type_changed'], result['room_type_change_rate']), (2, 1, 0.5))
        self.assertEqual(set(result), set(analysis.TRANSITION_FIELDS))

    def test_assignment_coverage_uses_all_assigned_ids(self):
        result = analysis.cohort_summary(records(), DATES, {'1','2','3','4','5'})
        self.assertEqual(result[0]['cohort_size'], 5)
        self.assertEqual(result[0]['missing_listings'], 2)
        self.assertEqual(result[0]['coverage'], 0.6)
        self.assertEqual(result[0]['cohort_basis'], 'assignment')
        self.assertEqual((result[0]['observed_hosts'], result[0]['host_id_unusable']), (2, 1))
        self.assertEqual(set(result[0]), set(analysis.SUMMARY_FIELDS))

    def test_observed_union_is_labelled_not_an_invented_assignment(self):
        result = analysis.cohort_summary(records(), DATES)
        self.assertEqual((result[0]['cohort_basis'], result[0]['cohort_size'], result[0]['coverage']),
                         ('observed_union', 4, 0.75))
        with self.assertRaisesRegex(ValueError, 'outside'):
            analysis.cohort_summary(records(), DATES, {'1'})

    def test_missing_values_are_excluded_from_matched_denominators(self):
        rows = [row(DATES[0], '1', '10', None), row(DATES[1], '1', '', 'Private room'),
                row(DATES[0], '2', '20.0'), row(DATES[1], '2', '21')]
        result = analysis.churn(rows, DATES)[0]
        self.assertEqual((result['host_comparable'], result['host_pairs_excluded']), (0, 2))
        self.assertIsNone(result['host_change_rate'])
        self.assertEqual((result['room_type_comparable'], result['room_type_pairs_excluded']), (1, 1))
        self.assertEqual(result['room_type_change_rate'], 0)

    def test_empty_and_one_snapshot_keep_undefined_distinct_from_zero(self):
        result = analysis.cohort_summary([], DATES, {'1'})
        self.assertEqual((result[0]['observed_listings'], result[0]['missing_listings'], result[0]['coverage']), (0, 1, 0))
        self.assertIsNone(analysis.cohort_summary([], DATES)[0]['coverage'])
        self.assertIsNone(analysis.churn([], DATES)[0]['entry_rate'])
        self.assertEqual(analysis.churn([], [DATES[0]]), [])

    def test_appearance_and_absence_rates_use_the_documented_bases(self):
        dates = [*DATES, '2026-07-01']
        result = analysis.churn([row(dates[0], '1'), row(dates[2], '2')], dates)
        self.assertIsNone(result[0]['entry_rate'])
        self.assertEqual(result[0]['exit_rate'], 1)
        self.assertEqual(result[1]['entry_rate'], 1)
        self.assertIsNone(result[1]['exit_rate'])

    def test_long_ids_remain_distinct_and_input_is_not_mutated(self):
        rows = [row(DATES[0], '1234567890123456788', '9876543210987654321'),
                row(DATES[1], '1234567890123456789', '9876543210987654321')]
        before = deepcopy(rows)
        result = analysis.churn(rows, DATES)[0]
        self.assertEqual((result['new'], result['retained'], result['disappeared']), (1, 0, 1))
        self.assertEqual(rows, before)
        self.assertEqual(analysis.cohort_summary(rows, DATES)[0]['observed_hosts'], 1)

    def test_bad_ids_dates_duplicate_keys_and_unexpected_snapshots_fail(self):
        cases = [(records(), []), (records(), list(reversed(DATES))), (records(), [DATES[0], DATES[0]]),
                 (records(), ['not-a-date']), ([row(DATES[0], '1'), row(DATES[0], '1')], DATES),
                 ([row(DATES[0], 1234567890123456789)], DATES), ([row('2026-07-01', '1')], DATES)]
        for rows, dates in cases:
            with self.subTest(rows=rows, dates=dates), self.assertRaises(ValueError):
                analysis.churn(rows, dates)

    def test_order_does_not_change_metrics_and_no_price_is_required(self):
        rows = records()
        self.assertEqual(analysis.churn(rows, DATES), analysis.churn(reversed(rows), DATES))
        self.assertEqual(analysis.cohort_summary(rows, DATES), analysis.cohort_summary(reversed(rows), DATES))


class MarketFigureTests(unittest.TestCase):
    def test_svg_data_and_denominators_match_analysis_without_mutation(self):
        tables = {'cohort_summary': analysis.cohort_summary(records(), DATES, {'1','2','3','4','5'}),
                  'churn_kpi': analysis.churn(records(), DATES)}
        original = deepcopy(tables)
        with tempfile.TemporaryDirectory() as temp:
            paths = viz_market.render(tables, Path(temp), {'city':'Toronto & <sample>', 'snapshots':DATES})
            self.assertEqual(len(paths), 2)
            summary = ET.parse(paths[0]).getroot()
            groups = [node for node in summary.iter() if 'data-observed' in node.attrib]
            self.assertEqual([(g.attrib['data-observed'],g.attrib['data-cohort']) for g in groups], [('3','5'),('3','5')])
            transitions = ET.parse(paths[1]).getroot()
            group = next(node for node in transitions.iter() if 'data-changed' in node.attrib)
            self.assertEqual((group.attrib['data-changed'],group.attrib['data-comparable'],group.attrib['data-rate']), ('1','2','0.5'))
            self.assertIn('&amp;', paths[0].read_text())
        self.assertEqual(tables, original)

    def test_no_comparable_host_is_na_and_empty_tables_still_render(self):
        unknown = [row(DATES[0], '1', None), row(DATES[1], '1', '')]
        with tempfile.TemporaryDirectory() as temp:
            paths = viz_market.render({'listings': unknown}, temp, {'city':'toronto','snapshots':DATES})
            text = ''.join(ET.parse(paths[1]).getroot().itertext())
            self.assertIn('N/A', text)
            self.assertNotIn('nan', paths[1].read_text().lower())
            paths = viz_market.render({'cohort_summary':[], 'churn_kpi':[]}, temp, {'city':'toronto','snapshots':DATES})
            self.assertIn('Cần ít nhất hai mốc', ''.join(ET.parse(paths[1]).getroot().itertext()))


class Tv1RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'configs').mkdir()
        self.cfg = json.loads((ROOT / 'configs/toronto.yaml').read_text())
        self.cfg['snapshots'] = DATES
        self.config = self.root / 'configs/toronto.yaml'
        self.config.write_text(json.dumps(self.cfg))

    def test_cli_demo_works_outside_repo_without_other_member_modules(self):
        result = subprocess.run([sys.executable, str(ROOT/'scripts/run_tv1.py'), '--config', str(self.config), '--demo'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        metadata = json.loads((self.root/'reports/generated/demo/tv1/run_metadata.json').read_text())
        self.assertEqual((metadata['input_stage'],metadata['data_code']), ('synthetic_demo','DEMO'))
        self.assertEqual(len(list((self.root/'figures/demo/tv1').glob('*.svg'))), 2)
        self.assertFalse((self.root/'data/processed/real').exists())

    def assignment(self):
        return SimpleNamespace(listing_ids={'1','2'}, areas={'1':'A01','2':'A01'},
                               code='DSE2049-C01-G10-toronto', fingerprint='test-workbook')

    def test_raw_projection_filters_assignment_and_does_not_read_price(self):
        for snapshot in DATES:
            path = self.root/'data/raw'/snapshot/'listings.csv.gz'
            path.parent.mkdir(parents=True)
            with gzip.open(path,'wt',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=['id','host_id','room_type'])
                writer.writeheader()
                writer.writerows([{'id':identity,'host_id':'10','room_type':'Private room'} for identity in ['1','2','999']])
        with patch.object(runner,'read_assignment',return_value=self.assignment()), contextlib.redirect_stdout(io.StringIO()):
            result = runner.run(self.config)
        self.assertEqual([r['observed_listings'] for r in result['tables']['cohort_summary']], [2,2])
        metadata=json.loads((result['reports']/'run_metadata.json').read_text())
        self.assertEqual(metadata['input_stage'], 'assigned_raw_identifier_projection')
        self.assertEqual(len(metadata['source_files']), 2)

    def test_cleaned_input_is_supported_but_duplicates_stop_before_output(self):
        source=self.root/'cleaned.csv'
        def write(records):
            with source.open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=['snapshot_date','listing_id','host_id','room_type'])
                writer.writeheader();writer.writerows(records)
        write([row(DATES[0],'1'),row(DATES[0],'1')])
        with patch.object(runner,'read_assignment',return_value=self.assignment()), self.assertRaisesRegex(ValueError,'Duplicate'):
            runner.run(self.config,listings_path=source)
        self.assertFalse((self.root/'data/processed').exists())
        write([row(DATES[0],'1'),row(DATES[1],'1','11')])
        with patch.object(runner,'read_assignment',return_value=self.assignment()), contextlib.redirect_stdout(io.StringIO()):
            result=runner.run(self.config,listings_path=source)
        self.assertEqual(result['tables']['churn_kpi'][0]['host_changed'],1)
        metadata=json.loads((result['reports']/'run_metadata.json').read_text())
        self.assertEqual(metadata['input_stage'],'provided_cleaned_listings')


if __name__ == '__main__':
    unittest.main()
