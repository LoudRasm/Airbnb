"""Synthetic annotation fixtures; no real review receives a machine-generated label."""
import csv
import gzip
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('annotation_tool', ROOT / 'scripts/label_reviews.py')
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class ManualAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'reviews.csv.gz'
        self.directory = self.root / 'packets'
        self.output = self.root / 'manual_labels.csv'
        self.identities = {str(9876543210987654000 + i) for i in range(100)}
        self.assignment = SimpleNamespace(code='DSE2049-C01-G10-toronto', fingerprint='fixture-workbook',
                                          snapshots=['2025-09-11', '2025-12-12', '2026-03-19', '2026-06-15'],
                                          manual_ids=self.identities, llm_ids=self.identities,
                                          review_ids=self.identities)
        self.records = [{'id': identity, 'listing_id': 'not-an-assigned-listing', 'date': '2025-01-01',
                         'comments': 'Synthetic fixture only: comma, quote " and\nnew line. Cảm ơn.'}
                        for identity in sorted(self.identities)]
        self.write_source(self.records)

    def write_source(self, records):
        with gzip.open(self.source, 'wt', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['id', 'listing_id', 'date', 'comments'])
            writer.writeheader()
            writer.writerows(records)

    def prepare(self):
        return tool.prepare(self.assignment, self.source, self.directory)

    def edit(self, member, callback):
        path = self.directory / f'{member}.json'
        packet = tool.read_json(path)
        callback(packet)
        tool.save_json(path, packet)

    def finish_synthetic_labels(self):
        for member in tool.TEAM:
            def fill(packet):
                for row in packet['labels']:
                    row['sentiment'] = 'positive'  # Synthetic test data, never the real packets.
            self.edit(member, fill)

    def test_prepare_exact_ids_blank_labels_and_no_listing_filter(self):
        before = tool.file_hash(self.source)
        manifest = self.prepare()
        seen = set()
        for member in tool.TEAM:
            packet = tool.read_json(self.directory / f'{member}.json')
            self.assertEqual(len(packet['labels']), 20)
            for row in packet['labels']:
                seen.add(row['review_id'])
                self.assertIsInstance(row['review_id'], str)
                self.assertEqual(row['sentiment'], '')
                self.assertEqual(row['listing_id'], 'not-an-assigned-listing')
                self.assertIn('\nnew line. Cảm ơn.', row['comments'])
        self.assertEqual(seen, self.identities)
        self.assertEqual(manifest['source_sha256'], before)
        self.assertEqual(tool.file_hash(self.source), before)

    def test_individual_check_needs_no_raw_or_workbook(self):
        self.prepare()
        self.source.unlink()
        _, selected, issues = tool.check(self.directory, 'tv2')
        self.assertEqual(len(selected), 20)
        self.assertEqual(len(issues), 20)  # Blank labels must never count as complete.

    def test_prepare_does_not_overwrite_existing_human_work(self):
        self.prepare()
        self.edit('tv2', lambda packet: packet['labels'][0].update(sentiment='mixed'))
        before = (self.directory / 'tv2.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'already exist'):
            self.prepare()
        self.assertEqual((self.directory / 'tv2.json').read_bytes(), before)

    def test_missing_duplicate_or_empty_raw_reviews_block_preparation(self):
        for records in [self.records[:-1], self.records + self.records[:1],
                        [{**self.records[0], 'comments': ' '}, *self.records[1:]]]:
            with self.subTest(size=len(records)):
                self.write_source(records)
                with self.assertRaises(ValueError):
                    self.prepare()
                self.assertFalse(self.directory.exists())

    def test_changed_ids_owner_and_source_text_are_rejected(self):
        self.prepare()
        path = self.directory / 'tv1.json'
        original = tool.read_json(path)
        changes = [lambda p: p['labels'][0].update(review_id=int(p['labels'][0]['review_id'])),
                   lambda p: p['labels'][0].update(review_id=p['labels'][1]['review_id']),
                   lambda p: p['labels'][0].update(comments='silently changed'),
                   lambda p: p.update(member='tv2')]
        for change in changes:
            with self.subTest(change=change):
                tool.save_json(path, original)
                self.edit('tv1', change)
                with self.assertRaises(ValueError):
                    tool.check(self.directory, 'tv1')

    def test_blank_invalid_and_uncertain_labels_cannot_merge(self):
        self.prepare()
        self.finish_synthetic_labels()
        for change in [dict(sentiment=''), dict(sentiment='neutral'), dict(needs_review=True)]:
            with self.subTest(change=change):
                self.edit('tv1', lambda p: p['labels'][0].update(sentiment='positive', needs_review=False))
                self.edit('tv1', lambda p: p['labels'][0].update(**change))
                self.output.write_text('review_id,sentiment\n', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'unresolved'):
                    tool.merge(self.directory, self.assignment, self.source, self.output)
                self.assertEqual(self.output.read_text(), 'review_id,sentiment\n')

    def test_final_merge_exact_100_ids_and_only_two_columns(self):
        self.prepare()
        self.finish_synthetic_labels()
        self.assertEqual(tool.merge(self.directory, self.assignment, self.source, self.output), 100)
        rows = list(tool.rows(self.output))
        self.assertEqual({row['review_id'] for row in rows}, self.identities)
        self.assertEqual(set(rows[0]), {'review_id', 'sentiment'})
        self.assertEqual(tool.merge(self.directory, self.assignment, self.source, self.output), 100)

    def test_changed_workbook_or_raw_source_cannot_merge(self):
        self.prepare()
        self.finish_synthetic_labels()
        self.assignment.fingerprint = 'different-workbook'
        with self.assertRaisesRegex(ValueError, 'workbook'):
            tool.merge(self.directory, self.assignment, self.source, self.output)
        self.assignment.fingerprint = 'fixture-workbook'
        self.write_source([{**row, 'comments': 'new version'} for row in self.records])
        with self.assertRaisesRegex(ValueError, 'source changed'):
            tool.merge(self.directory, self.assignment, self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_different_labels_are_not_overwritten(self):
        self.prepare()
        self.finish_synthetic_labels()
        previous = 'review_id,sentiment\n9876543210987654000,negative\n'
        self.output.write_text(previous, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'already contains'):
            tool.merge(self.directory, self.assignment, self.source, self.output)
        self.assertEqual(self.output.read_text(), previous)


if __name__ == '__main__':
    unittest.main()
