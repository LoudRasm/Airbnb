"""Test qa.clean_listings và các hàm QA bằng fixture nhỏ mô phỏng lỗi dữ liệu thật."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import qa

CFG = {
    'snapshots': ['2025-09-11', '2025-12-12', '2026-03-19', '2026-06-15'],
    'qa': {'price_max': 10000, 'min_nights_cap': 365, 'max_scrape_lag_days': 3,
           'room_types': ['Entire home/apt', 'Private room', 'Shared room', 'Hotel room'],
           'bbox': {'lat_min': 43.4, 'lat_max': 44.0, 'lon_min': -79.8, 'lon_max': -78.9}},
}
FINAL, EARLY = '2026-06-15', '2025-09-11'
HOODS = {'Annex', 'Junction'}


def raw(**kw):
    base = {'id': '1', 'host_id': '10', 'price': '$100.00', 'room_type': 'Private room',
            'latitude': '43.65', 'longitude': '-79.38', 'neighbourhood_cleansed': 'Annex',
            'analysis_area': 'A1', 'minimum_nights': '2', 'last_scraped': FINAL,
            'host_since': '2015-01-01', 'first_review': '2020-01-01', 'last_review': '2026-01-01'}
    base.update(kw)
    return base


def run(rows, snapshot=FINAL, cfg=CFG):
    cleaned, report = qa.clean_listings(iter(rows), snapshot, cfg)
    return cleaned, {r['rule']: r for r in report}


def cleaned_row(snapshot, listing_id, **kw):
    base = {'snapshot_date': snapshot, 'listing_id': listing_id, 'host_id': '10', 'price': 100.0,
            'room_type': 'Private room', 'analysis_area': 'A1', 'neighbourhood_cleansed': 'Annex',
            'latitude': 43.65, 'longitude': -79.38, 'qa_flags': ''}
    base.update(kw)
    return base


def flags(row):
    return set(filter(None, row['qa_flags'].split('|')))


class CleanListingsTests(unittest.TestCase):
    def test_clean_row_has_no_flags_and_exact_types(self):
        cleaned, report = run([raw()])
        row = cleaned[0]
        self.assertEqual(row['qa_flags'], '')
        self.assertEqual((row['listing_id'], row['host_id'], row['price']), ('1', '10', 100.0))
        self.assertIsInstance(row['latitude'], float)
        self.assertEqual(set(row), {c for c, *_ in qa.DICTIONARY})
        self.assertEqual(report['raw_input']['rows_after'], 1)

    def test_long_id_kept_exactly_and_float_like_id_flagged(self):
        big = '1234567890123456789'  # 19 chữ số: float sẽ làm mất độ chính xác
        cleaned, _ = run([raw(id=big), raw(id='123.0'), raw(id='1.2e+17')])
        self.assertEqual(cleaned[0]['listing_id'], big)
        self.assertEqual(cleaned[0]['qa_flags'], '')
        self.assertIn('id_format', flags(cleaned[1]))
        self.assertIn('id_format', flags(cleaned[2]))
        self.assertEqual(cleaned[1]['listing_id'], '123.0')  # không bị ép sang số

    def test_missing_id_is_dropped(self):
        cleaned, report = run([raw(id=' '), raw(id='2')])
        self.assertEqual([r['listing_id'] for r in cleaned], ['2'])
        self.assertEqual(report['id_missing']['affected_rows'], 1)
        self.assertEqual(report['id_missing']['action'], 'drop')
        self.assertEqual(report['id_missing']['rows_after'], 1)

    def test_duplicate_key_keeps_first_and_counts_conflict(self):
        cleaned, report = run([raw(id='5', price='$100'), raw(id='5', price='$900'), raw(id='6')])
        self.assertEqual([r['listing_id'] for r in cleaned], ['5', '6'])
        self.assertEqual(cleaned[0]['price'], 100.0)
        self.assertIn('duplicate_key', flags(cleaned[0]))
        self.assertEqual(report['duplicate_key']['affected_rows'], 1)
        self.assertIn('conflicting=1', report['duplicate_key']['action'])

    def test_critical_fields_flagged_per_column_in_one_rule(self):
        cleaned, report = run([raw(id='1', host_id=''), raw(id='2', room_type=''),
                               raw(id='3', analysis_area=''), raw(id='4')])
        self.assertEqual(flags(cleaned[0]), {'host_id_missing'})
        self.assertEqual(flags(cleaned[1]), {'room_type_missing'})
        self.assertEqual(flags(cleaned[2]), {'analysis_area_missing'})
        self.assertEqual(cleaned[3]['qa_flags'], '')
        rule = report['critical_field_missing']
        self.assertEqual(rule['affected_rows'], 3)
        self.assertIn('host_id_missing=1,room_type_missing=1,analysis_area_missing=1', rule['action'])

    def test_missing_price_is_error_only_at_final_snapshot(self):
        final, rep_final = run([raw(price='')], FINAL)
        early, rep_early = run([raw(price='', last_scraped=EARLY, last_review='2025-01-01')], EARLY)
        self.assertIn('price_missing_final', flags(final[0]))
        self.assertEqual(rep_final['price_missing_final']['affected_rows'], 1)
        self.assertEqual(early[0]['qa_flags'], '')
        self.assertEqual(rep_early['price_missing_final']['affected_rows'], 0)
        self.assertEqual(rep_early['price_missing_final']['action'], 'skip_not_final_snapshot')
        self.assertIsNone(early[0]['price'])

    def test_price_parsing_and_bad_values(self):
        cleaned, report = run([raw(id='1', price='$1,250.50'), raw(id='2', price='abc'),
                               raw(id='3', price='nan'), raw(id='4', price='$0.00'),
                               raw(id='5', price='-20')])
        by_id = {r['listing_id']: r for r in cleaned}
        self.assertEqual(by_id['1']['price'], 1250.5)
        self.assertIsNone(by_id['2']['price'])
        self.assertIsNone(by_id['3']['price'])  # nan không phải số hữu hạn
        self.assertIn('price_unparseable', flags(by_id['2']))
        self.assertIn('price_unparseable', flags(by_id['3']))
        for key in ('4', '5'):
            self.assertIsNone(by_id[key]['price'])
            self.assertIn('price_nonpositive', flags(by_id[key]))
        self.assertEqual(report['price_unparseable']['affected_rows'], 2)
        self.assertEqual(report['price_outlier']['affected_rows'], 2)
        self.assertIn('price_nonpositive=2,price_outlier_high=0', report['price_outlier']['action'])

    def test_price_outlier_nulled_and_median_changes(self):
        cleaned, report = run([raw(id='1', price='$100'), raw(id='2', price='$200'),
                               raw(id='3', price='$50000')])
        rule = report['price_outlier']
        self.assertEqual(rule['affected_rows'], 1)
        self.assertEqual(rule['median_price_before'], 200.0)  # median(100, 200, 50000)
        self.assertEqual(rule['median_price_after'], 150.0)   # median(100, 200)
        self.assertEqual(rule['rows_after'], 3)  # giữ dòng, chỉ bỏ giá
        self.assertIn('price_outlier_high', flags(cleaned[2]))
        self.assertIsNone(cleaned[2]['price'])

    def test_price_exactly_at_cap_is_not_outlier(self):
        cleaned, report = run([raw(price='$10,000.00')])
        self.assertEqual(cleaned[0]['price'], 10000.0)
        self.assertEqual(report['price_outlier']['affected_rows'], 0)

    def test_room_type_category_drift(self):
        cleaned, report = run([raw(id='1', room_type='Boat'), raw(id='2', room_type='Hotel room')])
        self.assertIn('room_type_unknown', flags(cleaned[0]))
        self.assertEqual(cleaned[0]['room_type'], 'Boat')  # giữ nguyên, chỉ gắn cờ
        self.assertEqual(cleaned[1]['qa_flags'], '')
        self.assertEqual(report['room_type_unknown']['affected_rows'], 1)

    def test_invalid_and_outside_coordinates(self):
        cleaned, report = run([raw(id='1', latitude='0', longitude='0'),
                               raw(id='2', latitude='95', longitude='-79'),
                               raw(id='3', latitude='', longitude='-79'),
                               raw(id='4', latitude='40.7', longitude='-74.0'),  # New York
                               raw(id='5')])
        by_id = {r['listing_id']: r for r in cleaned}
        for key in ('1', '2', '3'):
            self.assertIn('coordinates_invalid', flags(by_id[key]))
            self.assertIsNone(by_id[key]['latitude'])
            self.assertIsNone(by_id[key]['longitude'])
            self.assertNotIn('coordinates_outside_city', flags(by_id[key]))
        self.assertEqual(flags(by_id['4']), {'coordinates_outside_city'})
        self.assertEqual(by_id['4']['latitude'], 40.7)  # hợp lệ nhưng ngoài thành phố: chỉ cờ
        self.assertEqual(by_id['5']['qa_flags'], '')
        self.assertEqual(report['coordinates_invalid']['affected_rows'], 3)

    def test_bbox_rule_skipped_when_config_has_no_bbox(self):
        cfg = {**CFG, 'qa': {k: v for k, v in CFG['qa'].items() if k != 'bbox'}}
        cleaned, report = run([raw(latitude='40.7', longitude='-74.0')], cfg=cfg)
        self.assertEqual(cleaned[0]['qa_flags'], '')
        self.assertEqual(report['coordinates_outside_city']['action'], 'skip_no_bbox_in_config')

    def test_missing_neighbourhood_is_not_filled_with_analysis_area(self):
        cleaned, report = run([raw(neighbourhood_cleansed='', analysis_area='A3')])
        self.assertEqual(cleaned[0]['neighbourhood_cleansed'], '')
        self.assertEqual(cleaned[0]['analysis_area'], 'A3')
        self.assertEqual(flags(cleaned[0]), {'neighbourhood_missing'})  # trống thì không báo "không có trong geojson"
        self.assertEqual(report['critical_field_missing']['affected_rows'], 0)

    def test_referential_integrity_against_geojson_names(self):
        listings = [cleaned_row(FINAL, '1', neighbourhood_cleansed='Atlantis'),
                    cleaned_row(FINAL, '2', neighbourhood_cleansed='Junction'),
                    cleaned_row(FINAL, '3', neighbourhood_cleansed=''),            # rỗng: thuộc rule neighbourhood_missing
                    cleaned_row(EARLY, '1', neighbourhood_cleansed='Atlantis')]    # mốc không có tham chiếu: bỏ qua
        rows = qa.check_neighbourhood_reference(listings, {FINAL: HOODS})
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]['snapshot_date'], rows[0]['rule'], rows[0]['affected_rows']),
                         (FINAL, 'neighbourhood_not_in_reference', 1))
        self.assertEqual(rows[0]['rows_after'], 3)
        self.assertIn('reference_names=2', rows[0]['action'])

    def test_each_snapshot_uses_its_own_reference_names(self):
        listings = [cleaned_row(EARLY, '1', neighbourhood_cleansed='Junction'),
                    cleaned_row(FINAL, '1', neighbourhood_cleansed='Junction')]
        rows = {r['snapshot_date']: r for r in qa.check_neighbourhood_reference(
            listings, {EARLY: {'Annex'}, FINAL: {'Junction'}})}
        self.assertEqual((rows[EARLY]['affected_rows'], rows[FINAL]['affected_rows']), (1, 0))

    def test_neighbourhood_names_from_geojson(self):
        geo = {'features': [{'properties': {'neighbourhood': 'Annex', 'neighbourhood_group': ''}},
                            {'properties': {'neighbourhood': ' Junction '}}, {'properties': {}}]}
        self.assertEqual(qa.neighbourhood_names(geo), {'Annex', 'Junction'})

    def test_min_nights_outlier_and_multiple_flags_sorted(self):
        cleaned, _ = run([raw(minimum_nights='1000', host_id='', analysis_area='')])
        self.assertEqual(cleaned[0]['qa_flags'], 'analysis_area_missing|host_id_missing|min_nights_outlier')

    def test_min_nights_at_cap_is_not_outlier(self):
        cleaned, report = run([raw(minimum_nights='365')])
        self.assertEqual(report['min_nights_outlier']['affected_rows'], 0)
        self.assertEqual(cleaned[0]['qa_flags'], '')

    def test_invalid_dates(self):
        cleaned, report = run([raw(id='1', last_review='31/12/2025'),                       # sai định dạng
                               raw(id='2', first_review='2026-02-01', last_review='2026-01-01'),
                               raw(id='3', last_review='2026-12-31'),                       # sau last_scraped
                               raw(id='4', host_since='2027-01-01'),                         # sau last_scraped
                               raw(id='5', first_review='', last_review='', host_since=''),  # rỗng hợp lệ
                               raw(id='6')])
        by_id = {r['listing_id']: r for r in cleaned}
        self.assertEqual(flags(by_id['1']), {'date_unparseable'})
        for key in ('2', '3', '4'):
            self.assertEqual(flags(by_id[key]), {'date_order_invalid'}, key)
        self.assertEqual(by_id['5']['qa_flags'], '')
        self.assertEqual(by_id['6']['qa_flags'], '')
        self.assertEqual(report['date_invalid']['affected_rows'], 4)
        self.assertIn('date_unparseable=1,date_order_invalid=3', report['date_invalid']['action'])

    def test_scrape_date_offset_threshold(self):
        cleaned, report = run([raw(id='1', last_scraped='2026-06-18'),   # lệch 3 ngày: chấp nhận
                               raw(id='2', last_scraped='2026-06-19'),   # lệch 4 ngày
                               raw(id='3', last_scraped='2026-06-05'),   # lệch -10 ngày
                               raw(id='4', last_scraped='')])
        self.assertEqual([bool(flags(r) & {'scrape_date_offset'}) for r in cleaned], [False, True, True, False])
        self.assertEqual(report['scrape_date_offset']['affected_rows'], 2)

    def test_missing_required_column_reported_and_raw_not_mutated(self):
        original = raw()
        del original['room_type']
        before = dict(original)
        cleaned, report = run([original])
        self.assertIn('room_type', report['raw_input']['action'])
        self.assertEqual(cleaned[0]['room_type'], '')
        self.assertIn('room_type_missing', flags(cleaned[0]))
        self.assertEqual(original, before)

    def test_report_schema_and_rows_after_monotonic(self):
        _, report = qa.clean_listings(iter([raw(id=' '), raw(id='2'), raw(id='2')]), FINAL, CFG)
        fields = {'snapshot_date', 'rule', 'affected_rows', 'action', 'rows_after',
                  'median_price_before', 'median_price_after'}
        self.assertTrue(all(set(r) == fields for r in report))
        self.assertEqual([r['rule'] for r in report], list(qa.RULE_ORDER))
        after = [r['rows_after'] for r in report]
        self.assertEqual(after, sorted(after, reverse=True))
        self.assertEqual((after[0], after[-1]), (3, 1))

    def test_signature_matches_contract_three_arguments(self):
        cleaned, report = qa.clean_listings(iter([raw()]), FINAL, CFG)  # đúng hợp đồng CONTRACTS.md
        self.assertEqual(len(cleaned), 1)
        self.assertEqual([r['rule'] for r in report], list(qa.RULE_ORDER))

    def test_empty_input(self):
        cleaned, report = run([])
        self.assertEqual(cleaned, [])
        self.assertTrue(all(r['affected_rows'] == 0 for r in report.values()))

    def test_compare_schemas(self):
        out = qa.compare_schemas({'s1': ['id', 'a'], 's2': ['id', 'a', 'b'], 's3': ['id', 'b']})
        self.assertEqual([(r['snapshot_date'], r['affected_rows']) for r in out], [('s2', 1), ('s3', 1)])
        self.assertIn('added=b', out[0]['action'])
        self.assertIn('dropped=a', out[1]['action'])


class CrossSnapshotTests(unittest.TestCase):
    S1, S2, S3 = CFG['snapshots'][:3]

    def by_rule(self, rows, snapshot):
        return {r['rule']: r for r in rows if r['snapshot_date'] == snapshot}

    def test_detects_each_kind_of_change_between_adjacent_snapshots(self):
        listings = [
            cleaned_row(self.S1, '1'), cleaned_row(self.S2, '1', host_id='99'),
            cleaned_row(self.S1, '2'), cleaned_row(self.S2, '2', room_type='Entire home/apt'),
            cleaned_row(self.S1, '3'), cleaned_row(self.S2, '3', neighbourhood_cleansed='Junction'),
            cleaned_row(self.S1, '4'), cleaned_row(self.S2, '4', latitude=43.70),  # ~5.6 km
            cleaned_row(self.S1, '5'), cleaned_row(self.S2, '5'),                  # không đổi
        ]
        got = self.by_rule(qa.cross_snapshot_checks(listings, CFG), self.S2)
        self.assertEqual({r for r in got}, set(qa.CROSS_RULES))
        self.assertEqual(got['cross_host_id_changed']['affected_rows'], 1)
        self.assertEqual(got['cross_coordinates_moved']['affected_rows'], 1)
        self.assertEqual(got['cross_category_changed']['affected_rows'], 2)  # listing 2 (room) + 3 (khu vực)
        self.assertIn('room_type=1,neighbourhood=1', got['cross_category_changed']['action'])
        for rule in qa.CROSS_RULES:
            self.assertEqual(got[rule]['rows_after'], 5)
            self.assertIn('compared=5', got[rule]['action'])

    def test_listing_changing_both_room_and_area_counts_once(self):
        listings = [cleaned_row(self.S1, '1'),
                    cleaned_row(self.S2, '1', room_type='Shared room', neighbourhood_cleansed='Junction')]
        got = self.by_rule(qa.cross_snapshot_checks(listings, CFG), self.S2)
        self.assertEqual(got['cross_category_changed']['affected_rows'], 1)
        self.assertIn('room_type=1,neighbourhood=1', got['cross_category_changed']['action'])

    def test_small_shift_and_missing_coordinates_are_not_counted(self):
        listings = [cleaned_row(self.S1, '1'), cleaned_row(self.S2, '1', latitude=43.6505),  # ~55 m
                    cleaned_row(self.S1, '2', latitude=None, longitude=None), cleaned_row(self.S2, '2')]
        got = self.by_rule(qa.cross_snapshot_checks(listings, CFG), self.S2)
        self.assertEqual(got['cross_coordinates_moved']['affected_rows'], 0)

    def test_only_listings_present_in_both_snapshots_are_compared(self):
        listings = [cleaned_row(self.S1, '1'), cleaned_row(self.S2, '1'),
                    cleaned_row(self.S1, '2'), cleaned_row(self.S2, '3', host_id='77')]  # 2 biến mất, 3 mới
        got = self.by_rule(qa.cross_snapshot_checks(listings, CFG), self.S2)
        self.assertEqual(got['cross_host_id_changed']['affected_rows'], 0)
        self.assertIn('compared=1', got['cross_host_id_changed']['action'])

    def test_compares_adjacent_pairs_in_config_order_not_input_order(self):
        listings = [cleaned_row(self.S3, '1', host_id='3'), cleaned_row(self.S1, '1', host_id='1'),
                    cleaned_row(self.S2, '1', host_id='1')]  # input xáo trộn; chỉ S2 -> S3 đổi host
        rows = qa.cross_snapshot_checks(listings, CFG)
        self.assertEqual(self.by_rule(rows, self.S2)['cross_host_id_changed']['affected_rows'], 0)
        self.assertEqual(self.by_rule(rows, self.S3)['cross_host_id_changed']['affected_rows'], 1)
        self.assertEqual({r['snapshot_date'] for r in rows}, {self.S2, self.S3})

    def test_single_snapshot_has_nothing_to_compare(self):
        self.assertEqual(qa.cross_snapshot_checks([cleaned_row(self.S1, '1')], CFG), [])

    def test_distance_helper_matches_known_value(self):
        self.assertAlmostEqual(qa._km(43.0, -79.0, 43.01, -79.0), 1.112, places=2)


class ProfileAndImpactTests(unittest.TestCase):
    def test_missing_rates_distinguish_missing_column_from_empty_value(self):
        rows = [raw(price=''), raw(price='$10'), raw(price='')]
        got = {r['column']: r for r in qa.missing_rates(rows, FINAL, ['price', 'room_type', 'nonexistent'])}
        self.assertEqual((got['price']['missing'], got['price']['missing_rate']), (2, 0.6667))
        self.assertTrue(got['price']['column_present'])
        self.assertEqual(got['room_type']['missing'], 0)
        self.assertFalse(got['nonexistent']['column_present'])
        self.assertEqual(got['nonexistent']['missing'], 3)

    def test_kpi_impact_before_and_after(self):
        rows = [raw(id='1', host_id='10', room_type='Entire home/apt', price='$100'),
                raw(id='2', host_id='10', room_type='Private room', price='$200'),
                raw(id='3', host_id='11', room_type='Entire home/apt', price='$90000'),  # nulled
                raw(id='3', host_id='11', room_type='Entire home/apt', price='$90000')]  # duplicate, dropped
        cleaned, _ = run(rows)
        got = {r['kpi']: r for r in qa.kpi_impact(rows, cleaned, FINAL)}
        self.assertEqual((got['supply']['before'], got['supply']['after']), (4, 3))
        self.assertEqual((got['price_n']['before'], got['price_n']['after']), (4, 2))
        self.assertEqual(got['median_price']['before'], 45100.0)  # median(100, 200, 90000, 90000) = (200+90000)/2
        self.assertEqual(got['median_price']['after'], 150.0)    # median(100, 200)
        self.assertAlmostEqual(got['entire_home_share']['before'], 0.75)
        self.assertAlmostEqual(got['entire_home_share']['after'], 2 / 3)
        self.assertAlmostEqual(got['multi_listing_host_share']['before'], 1.0)  # dòng trùng làm host 11 trông có 2 listing: 4/4
        self.assertAlmostEqual(got['multi_listing_host_share']['after'], 2 / 3)  # sau dedupe chỉ host 10 nhiều listing: 2/3
        self.assertAlmostEqual(got['supply']['delta'], -1)

    def test_kpi_impact_unchanged_when_nothing_flagged_changes_values(self):
        rows = [raw(id='1'), raw(id='2', host_id='11')]
        cleaned, _ = run(rows)
        self.assertTrue(all(r['delta'] == 0 for r in qa.kpi_impact(rows, cleaned, FINAL)))


class RunListingsQaAndEdaTests(unittest.TestCase):
    def test_run_listings_qa_combines_all_checks_over_snapshots(self):
        s1, s2 = CFG['snapshots'][:2]
        raw_by = {s1: [raw(id='1', last_scraped=s1, last_review='2025-01-01'), raw(id='2', last_scraped=s1, last_review='2025-01-01')],
                  s2: [raw(id='1', host_id='99', last_scraped=s2, last_review='2025-01-01'),
                       raw(id='2', last_scraped=s2, last_review='2025-01-01', neighbourhood_cleansed='Atlantis')]}
        out = qa.run_listings_qa(raw_by, CFG, {s1: HOODS, s2: HOODS})
        self.assertEqual(len(out['cleaned']), 4)
        rules = {(r['snapshot_date'], r['rule']): r for r in out['qa_report']}
        self.assertEqual(rules[(s2, 'cross_host_id_changed')]['affected_rows'], 1)
        self.assertEqual(rules[(s2, 'neighbourhood_not_in_reference')]['affected_rows'], 1)
        self.assertEqual(rules[(s2, 'schema_drift')]['affected_rows'], 0)
        self.assertEqual(rules[(s1, 'raw_input')]['rows_after'], 2)
        self.assertEqual({r['snapshot_date'] for r in out['kpi_impact']}, {s1, s2})
        self.assertEqual({r['snapshot_date'] for r in out['missingness']}, {s1, s2})

    def test_run_listings_qa_skips_snapshots_without_data_and_reference(self):
        out = qa.run_listings_qa({FINAL: [raw()]}, CFG)
        self.assertEqual(len(out['cleaned']), 1)
        self.assertFalse(any(r['rule'] == 'neighbourhood_not_in_reference' for r in out['qa_report']))

    def test_eda_profile_counts_each_flag_and_clean_rows(self):
        from airbnb import eda
        rows = [cleaned_row(FINAL, '1', qa_flags='host_id_missing|min_nights_outlier'),
                cleaned_row(FINAL, '2', qa_flags='host_id_missing'),
                cleaned_row(FINAL, '3'), cleaned_row(EARLY, '1')]
        got = {(r['snapshot_date'], r['qa_flags']): r['count'] for r in eda.profile(rows)}
        self.assertEqual(got, {(FINAL, 'host_id_missing'): 2, (FINAL, 'min_nights_outlier'): 1,
                               (FINAL, 'none'): 1, (EARLY, 'none'): 1})
        self.assertEqual(eda.profile([]), [])


class CatalogTests(unittest.TestCase):
    def test_every_emitted_rule_has_catalog_entry_with_four_fields(self):
        emitted = set(qa.RULE_ORDER) | set(qa.CROSS_RULES) | {qa.SCHEMA_RULE, qa.REFERENCE_RULE}
        self.assertEqual(set(qa.RULES), emitted)
        catalog = qa.rule_catalog()
        self.assertEqual(len(catalog), len(emitted))
        for entry in catalog:
            self.assertTrue(all(entry[k] for k in ('rule', 'group', 'condition', 'reason', 'action')), entry)

    def test_rule_count_within_assignment_range(self):
        # Đề: khoảng 15–20 rule (không tính dòng cơ sở raw_input).
        self.assertTrue(15 <= len(qa.RULES) - 1 <= 20, len(qa.RULES) - 1)

    def test_data_dictionary_covers_cleaned_schema_in_pipeline_order(self):
        self.assertEqual([r['column'] for r in qa.data_dictionary()],
                         ['snapshot_date', 'listing_id', 'host_id', 'price', 'room_type', 'analysis_area',
                          'neighbourhood_cleansed', 'latitude', 'longitude', 'qa_flags'])
        self.assertTrue(all(r['description'] and r['type'] for r in qa.data_dictionary()))

    def test_flags_named_in_dictionary_rules_exist(self):
        # Tên rule nhắc trong data dictionary phải là rule thật hoặc tên cờ con của một rule.
        known = set(qa.RULES) | {'host_id_missing', 'room_type_missing', 'analysis_area_missing',
                                 'price_nonpositive', 'price_outlier_high'}
        for _, _, _, _, rules in qa.DICTIONARY:
            for name in (x.strip() for x in rules.split(',')):
                if name.startswith(('Khóa', 'tất cả')):
                    continue
                self.assertIn(name, known, name)


if __name__ == '__main__':
    unittest.main()
