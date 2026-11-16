"""Test viz_qa: các hàm tính số liệu cho hình và việc ghi ba file SVG hợp lệ."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import viz_qa

EARLY, FINAL = '2025-09-11', '2026-06-15'
CFG = {'snapshots': [EARLY, FINAL], 'qa': {'room_types': ['Entire home/apt', 'Private room']}}


def listing(snapshot, listing_id, price=100.0, room_type='Entire home/apt', neighbourhood='Annex'):
    return {'snapshot_date': snapshot, 'listing_id': listing_id, 'host_id': '1', 'price': price,
            'room_type': room_type, 'analysis_area': 'A1', 'neighbourhood_cleansed': neighbourhood,
            'latitude': 43.65, 'longitude': -79.38, 'qa_flags': ''}


def report_row(snapshot, rule, affected, rows_after=4, before=100.0, after=100.0):
    return {'snapshot_date': snapshot, 'rule': rule, 'affected_rows': affected, 'action': 'flag',
            'rows_after': rows_after, 'median_price_before': before, 'median_price_after': after}


def tables():
    listings = [listing(EARLY, '1'), listing(EARLY, '2', price=None, room_type='Private room'),
                listing(FINAL, '1'), listing(FINAL, '2', price=None, room_type='Hotel room'),
                listing(FINAL, '3', price='', neighbourhood='')]
    qa_report = [
        report_row(EARLY, 'raw_input', 2, 2, 100.0, 100.0), report_row(EARLY, 'price_outlier', 0, 2, 100.0, 100.0),
        report_row(FINAL, 'raw_input', 3, 3, 120.0, 120.0), report_row(FINAL, 'id_missing', 1, 2, 120.0, 120.0),
        report_row(FINAL, 'price_missing_final', 2, 2, 120.0, 150.0), report_row(FINAL, 'cross_host_id_changed', 7),
        # dòng do owner khác ghi vào qa_report: không được lẫn vào rule của QA
        {'snapshot_date': FINAL, 'rule': 'calendar_gap', 'affected_rows': 9, 'action': 'owner_defined',
         'rows_after': '', 'median_price_before': '', 'median_price_after': ''},
    ]
    return {'listings': listings, 'qa_report': qa_report}


class DataFunctionTests(unittest.TestCase):
    def test_rule_matrix_keeps_only_shown_rules_and_distinguishes_zero_from_not_run(self):
        matrix = viz_qa.rule_matrix(tables()['qa_report'], [EARLY, FINAL])
        self.assertEqual(matrix[(EARLY, 'price_outlier')], 0)
        self.assertEqual(matrix[(FINAL, 'id_missing')], 1)
        self.assertEqual(matrix[(FINAL, 'cross_host_id_changed')], 7)
        self.assertNotIn((EARLY, 'cross_host_id_changed'), matrix)  # không chạy: không có khóa
        self.assertNotIn((FINAL, 'raw_input'), matrix)
        self.assertNotIn((FINAL, 'calendar_gap'), matrix)

    def test_missing_rates_count_none_and_empty_string(self):
        rates = viz_qa.missing_rates(tables()['listings'], [EARLY, FINAL])
        self.assertEqual(rates[(EARLY, 'price')], 0.5)
        self.assertAlmostEqual(rates[(FINAL, 'price')], 2 / 3)
        self.assertAlmostEqual(rates[(FINAL, 'neighbourhood_cleansed')], 1 / 3)
        self.assertEqual(rates[(FINAL, 'host_id')], 0)

    def test_missing_rates_skip_snapshot_without_rows(self):
        rates = viz_qa.missing_rates(tables()['listings'], [EARLY, '2030-01-01'])
        self.assertTrue(all(snapshot == EARLY for snapshot, _ in rates))

    def test_room_type_shares_fold_unknown_types_into_other(self):
        shares, labels = viz_qa.room_type_shares(tables()['listings'], [EARLY, FINAL], CFG['qa']['room_types'])
        self.assertEqual(labels, ['Entire home/apt', 'Private room', 'Khác / rỗng'])
        self.assertEqual(dict(shares[EARLY]), {'Entire home/apt': 0.5, 'Private room': 0.5, 'Khác / rỗng': 0.0})
        self.assertAlmostEqual(dict(shares[FINAL])['Khác / rỗng'], 1 / 3)
        for rows in shares.values():
            self.assertAlmostEqual(sum(share for _, share in rows), 1.0)

    def test_kpi_pairs_use_raw_input_as_before_and_last_clean_rule_as_after(self):
        pairs = viz_qa.kpi_pairs(tables()['qa_report'], [EARLY, FINAL])
        self.assertEqual(pairs[EARLY], {'supply_before': 2, 'supply_after': 2,
                                        'median_before': 100.0, 'median_after': 100.0})
        # rule so sánh chéo và dòng owner_defined không phải bước cuối của clean_listings
        self.assertEqual(pairs[FINAL], {'supply_before': 3, 'supply_after': 2,
                                        'median_before': 120.0, 'median_after': 150.0})

    def test_kpi_pairs_empty_median_becomes_none(self):
        rows = [report_row(FINAL, 'raw_input', 3, 3, '', ''), report_row(FINAL, 'id_missing', 0, 3, '', '')]
        pair = viz_qa.kpi_pairs(rows, [FINAL])[FINAL]
        self.assertIsNone(pair['median_before'])
        self.assertIsNone(pair['median_after'])

    def test_axis_returns_round_ticks_covering_the_value(self):
        self.assertEqual(viz_qa._axis(1100), (1250, 250))
        self.assertEqual(viz_qa._axis(235), (250, 50))
        self.assertEqual(viz_qa._axis(0), (1, 1))
        for value in (3, 47, 999, 12345):
            top, step = viz_qa._axis(value)
            self.assertGreaterEqual(top, value)
            self.assertEqual(top % step, 0)


class HeadlineTests(unittest.TestCase):
    """Tiêu đề hình nêu kết luận (bài 12 và 14) và số trong tiêu đề tính từ chính dữ liệu."""

    def test_snapshot_sizes_use_raw_input_then_fall_back_to_listings(self):
        data = tables()
        self.assertEqual(viz_qa.snapshot_sizes(data['qa_report'], data['listings'], [EARLY, FINAL]), {EARLY: 2, FINAL: 3})
        self.assertEqual(viz_qa.snapshot_sizes([], data['listings'], [EARLY, FINAL]), {EARLY: 2, FINAL: 3})

    def test_price_counts_exclude_none_and_empty_string(self):
        self.assertEqual(viz_qa.price_counts(tables()['listings'], [EARLY, FINAL]), {EARLY: 1, FINAL: 1})

    def test_rules_headline_counts_flagged_rows_and_names_top_rule(self):
        data = tables()
        matrix = viz_qa.rule_matrix(data['qa_report'], [EARLY, FINAL])
        title, extra = viz_qa.headline_rules(matrix, {EARLY: 2, FINAL: 3})
        self.assertEqual(title, 'QA gắn cờ 3/5 dòng (60.0%), nhiều nhất ở price_missing_final')
        self.assertIn('cross_host_id_changed = 7', extra)

    def test_rules_headline_when_nothing_is_flagged(self):
        title, extra = viz_qa.headline_rules({(EARLY, 'id_missing'): 0}, {EARLY: 10})
        self.assertEqual(title, 'Không rule nào trong 14 rule của mỗi mốc tìm thấy dòng lỗi (10 dòng)')
        self.assertEqual(extra, '')

    def test_missingness_headline_names_columns_and_reports_drift(self):
        data = tables()
        rates = viz_qa.missing_rates(data['listings'], [EARLY, FINAL])
        shares, _ = viz_qa.room_type_shares(data['listings'], [EARLY, FINAL], CFG['qa']['room_types'])
        title = viz_qa.headline_missingness(rates, shares)
        self.assertIn('Thiếu dữ liệu ở 2/7 cột (neighbourhood_cleansed, price)', title)
        self.assertIn('lệch tối đa', title)  # Entire home 50% -> 33%: cơ cấu có đổi

    def test_missingness_headline_for_clean_stable_data(self):
        listings = [listing(EARLY, '1'), listing(FINAL, '1')]
        rates = viz_qa.missing_rates(listings, [EARLY, FINAL])
        shares, _ = viz_qa.room_type_shares(listings, [EARLY, FINAL], CFG['qa']['room_types'])
        self.assertEqual(viz_qa.headline_missingness(rates, shares),
                         'Không cột nào thiếu dữ liệu; cơ cấu room_type không đổi giữa các mốc')

    def test_kpi_headline_unchanged_versus_changed(self):
        same = {EARLY: {'supply_before': 5, 'supply_after': 5, 'median_before': 10.0, 'median_after': 10.0}}
        self.assertEqual(viz_qa.headline_kpi(same)[0], 'QA không làm đổi KPI: supply và median giá giữ nguyên ở mọi mốc')
        title, supply, median = viz_qa.headline_kpi(viz_qa.kpi_pairs(tables()['qa_report'], [EARLY, FINAL]))
        self.assertEqual((supply, median), (1, 30.0))
        self.assertEqual(title, 'QA đổi supply tối đa 1 listing và median giá tối đa 30.0 CAD')


class RenderTests(unittest.TestCase):
    def render(self, data=None, cfg=CFG):
        folder = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in folder.iterdir()] or folder.rmdir())
        return viz_qa.render(data or tables(), folder, cfg)

    def test_render_writes_three_well_formed_svg_files(self):
        paths = self.render()
        self.assertEqual([p.name for p in paths], list(viz_qa.FIGURES))
        for path in paths:
            root = ElementTree.fromstring(path.read_text(encoding='utf-8'))  # parse được = XML hợp lệ
            self.assertTrue(root.tag.endswith('svg'))
            texts = ''.join(root.itertext())
            self.assertTrue(root.find('{http://www.w3.org/2000/svg}title').text)  # có tiêu đề cho trình đọc
            self.assertIn('Nguồn', texts)  # có caption nêu nguồn số liệu

    def test_rule_figure_shows_counts_and_not_run_marks(self):
        text = ''.join(ElementTree.fromstring(self.render()[0].read_text(encoding='utf-8')).itertext())
        for rule in viz_qa.RULES_SHOWN:
            self.assertIn(rule, text)
        self.assertIn('7', text)
        self.assertIn('–', text)

    def test_kpi_figure_labels_match_the_report_numbers(self):
        text = ''.join(ElementTree.fromstring(self.render()[2].read_text(encoding='utf-8')).itertext())
        self.assertIn('120.0', text)
        self.assertIn('150.0', text)

    def test_every_figure_has_conclusion_title_sample_size_source_and_limit(self):
        cfg = {**CFG, 'city': 'toronto', 'assignment': {'group': 10}}
        for path in self.render(cfg=cfg):
            root = ElementTree.fromstring(path.read_text(encoding='utf-8'))
            texts = ''.join(root.itertext())
            title = root.find('{http://www.w3.org/2000/svg}title').text
            self.assertNotIn('theo snapshot', title)  # tiêu đề nêu kết luận, không chỉ gọi tên biểu đồ
            self.assertRegex(title, r'\d')  # có con số làm căn cứ
            self.assertIn('n=', texts)  # cỡ mẫu
            self.assertIn('Nguồn: Inside Airbnb, Toronto', texts)
            self.assertIn('mốc chụp', texts)
            self.assertIn('Giới hạn', texts)
            self.assertIn('nhóm 10', texts)

    def test_render_does_not_mutate_input_tables(self):
        data = tables()
        before = copy.deepcopy(data)
        self.render(data)
        self.assertEqual(data, before)

    def test_render_escapes_markup_in_labels(self):
        cfg = {'snapshots': [EARLY, FINAL], 'qa': {'room_types': ['A&B <x>']}}
        for path in self.render(cfg=cfg):
            ElementTree.fromstring(path.read_text(encoding='utf-8'))

    def test_render_works_with_no_rows(self):
        paths = self.render({'listings': [], 'qa_report': []})
        self.assertEqual(len(paths), 3)

    def test_render_requires_qa_report_and_listings(self):
        with self.assertRaises(ValueError):
            viz_qa.render({'listings': []}, Path(tempfile.mkdtemp()), CFG)



if __name__ == '__main__':
    unittest.main()
