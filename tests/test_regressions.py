"""Regression scenarios from the 2026-11-16 audit; all data/API replies here are synthetic."""
import csv
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest
from airbnb import calendar, kpi, llm, pipeline, reviews, viz_qa
from airbnb.io import load_config, rows
from airbnb.loading import read_assignment

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def case(tmp_path):
    cfg = json.loads((ROOT / 'configs/toronto.yaml').read_text())
    (tmp_path / 'configs').mkdir()
    shutil.copytree(ROOT / 'data/samples/demo', tmp_path / 'relocated_input')
    cfg['paths']['raw'] = 'relocated_input'
    cfg['assignment']['manifest'] = 'scope.json'
    cfg['llm']['sample_size'] = 1
    manifest = json.loads((ROOT / 'data/reference/assignment.json').read_text())
    listing_ids = {r['id'] for snap in cfg['snapshots'] for r in rows(tmp_path / 'relocated_input' / snap / 'listings.csv.gz')}
    manifest.update(listing_ids=sorted(listing_ids), areas={lid: 'A01' for lid in listing_ids},
                    review_ids=['100', '101', '102'], llm_ids=['100'], manual_ids=['100'])
    (tmp_path / 'scope.json').write_text(json.dumps(manifest))
    labels = tmp_path / cfg['paths']['manual_labels']
    labels.parent.mkdir(parents=True)
    labels.write_text('review_id,sentiment\n100,positive\n')
    config = tmp_path / 'configs/toronto.yaml'
    config.write_text(json.dumps(cfg))
    return tmp_path, cfg, config


def make_test_cache(root, cfg):
    collected = {}
    for snap in cfg['snapshots']:
        reviews.collect(rows(root / cfg['paths']['raw'] / snap / 'reviews.csv.gz'), snap, collected)
    # Fake API is used only to create a cache in pytest's temporary folder.
    response = json.dumps({'sentiment': 'positive', 'language': 'en', 'positive_aspects': ['host'], 'negative_aspects': []})
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'fixture-only'}), patch.object(llm, 'call_gemini_api', return_value=response):
        llm.analyze(list(collected.values()), cfg, root, {'100'}, allow_api=True)


def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}


def test_cache_miss_never_calls_api_even_if_key_is_present(tmp_path):
    cfg = {'llm': {'model': 'fixture', 'aspects': ['host'], 'sample_size': 1}}
    with patch.dict(os.environ, {'GEMINI_API_KEY': 'fixture-only'}), patch.object(llm, 'call_gemini_api') as api:
        with pytest.raises(RuntimeError, match='cache thiếu 1/1'):
            llm.analyze([{'review_id': '1234567890123456789', 'comments': 'Helpful host'}], cfg, tmp_path)
        api.assert_not_called()
    assert not (tmp_path / 'data').exists()


def test_full_cache_run_offline_then_skip_preserves_all_full_outputs(case):
    root, cfg, config = case
    make_test_cache(root, cfg)
    label_hash = hashes(root / 'data/samples')
    cache_hash = hashes(root / 'data/processed')
    with patch.dict(os.environ, {}, clear=True), patch('urllib.request.urlopen', side_effect=AssertionError('Offline verification')):
        tables = pipeline.run(config, no_download=True)
        assert len(tables['evaluation']) == 2
        assert all(r['paired_n'] == 1 for r in tables['evaluation'])
        assert tables['guest_kpi'][-1]['metric'] == 'area_guest_issue_rate'
        before = {name: hashes(root / name / 'real') for name in ('data/processed', 'reports/generated', 'figures')}
        pipeline.run(config, skip_llm=True, no_download=True)
        for name, files in before.items():
            now = hashes(root / name / 'real')
            assert all(now[p] == value for p, value in files.items())
        assert not (root / 'data/processed/real/non_llm/llm_reviews.csv').exists()
    assert hashes(root / 'data/samples') == label_hash
    assert all(hashes(root / 'data/processed')[p] == h for p, h in cache_hash.items())


def test_failed_render_preserves_published_results(case):
    root, cfg, config = case
    make_test_cache(root, cfg)
    sentinel = root / 'data/processed/real/listings.csv'
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text('previous successful run')
    with patch.object(pipeline.viz, 'render_all', side_effect=ValueError('bad plot')):
        with pytest.raises(ValueError, match='bad plot'):
            pipeline.run(config, no_download=True)
    assert sentinel.read_text() == 'previous successful run'
    assert not (sentinel.parent / 'llm_reviews.csv').exists()


def test_extra_snapshot_and_relocated_raw_use_config_only(case):
    root, cfg, config = case
    source, extra = cfg['snapshots'][0], '2030-01-01'
    folder = root / cfg['paths']['raw'] / extra
    shutil.copytree(root / cfg['paths']['raw'] / source, folder)
    cfg['snapshots'].append(extra)
    config.write_text(json.dumps(cfg))
    with patch('urllib.request.urlopen', side_effect=AssertionError('No network')):
        first = pipeline.run(config, skip_llm=True, no_download=True)
    assert {r['snapshot_date'] for r in first['market_kpi']} == set(cfg['snapshots'])
    assert (root / 'figures/real/non_llm/viz1_median_price.png').exists()
    cfg['snapshots'] = [extra]
    config.write_text(json.dumps(cfg))
    with patch('urllib.request.urlopen', side_effect=AssertionError('No network')):
        tables = pipeline.run(config, skip_llm=True, no_download=True)
    assert {r['snapshot_date'] for r in tables['market_kpi']} == {extra}
    assert all(r['median_price'] is None and r['price_n'] == 0 for r in tables['market_kpi'])
    # No price chart for a run that does not contain the assigned price snapshot.
    assert not (root / 'figures/real/non_llm/viz1_median_price.png').exists()
    assert (root / 'figures/real/non_llm/viz3_compare.png').exists()


def test_cache_text_changed_rejected_without_api(case):
    root, cfg, config = case
    make_test_cache(root, cfg)
    with patch.object(llm, 'call_gemini_api') as api, pytest.raises(RuntimeError, match='cache thiếu'):
        llm.analyze([{'review_id': '100', 'comments': 'A different source text'}], cfg, root, {'100'})
    api.assert_not_called()


def test_missing_listing_calendar_stays_in_coverage_denominator():
    data = [{'listing_id': '1', 'date': '2026-06-15', 'available': 't'},
            {'listing_id': '1', 'date': '2026-06-16', 'available': 'f'}]
    summary, issues = calendar.aggregate(iter(data), '2026-06-15', 2, {'1', '2'})
    assert len(summary) == 2 and summary[1]['availability_rate'] is None
    assert issues['missing_calendar_days'] == 2
    metrics = calendar.metrics(summary, [{'snapshot_date': '2026-06-15', 'listing_id': lid, 'analysis_area': 'A01'} for lid in ('1', '2')], {})[0]
    assert metrics['expected_days'] == 4 and metrics['listing_n'] == 2
    assert metrics['coverage_rate'] == .5 and metrics['availability_rate'] == .5


def test_invalid_calendar_value_does_not_hide_later_valid_duplicate():
    data = [{'listing_id': '1', 'date': '2026-06-15', 'available': state} for state in ('?', 't')]
    summary, issues = calendar.aggregate(data, '2026-06-15', 1, {'1'})
    assert summary[0]['observed_days'] == 1 and summary[0]['availability_rate'] == 1
    assert issues == {'invalid_available': 1}
    with pytest.raises(ValueError, match='positive'):
        calendar.aggregate([], '2026-06-15', 0, {'1'})


def test_neighbourhood_supply_and_shares_do_not_require_price():
    listings = [{'listing_id': str(i), 'host_id': '', 'snapshot_date': '2026-06-15',
                 'price': p, 'analysis_area': 'A01', 'neighbourhood_cleansed': 'Annex', 'room_type': ''}
                for i, p in enumerate((100, None), 1)]
    result = kpi.neighbourhood_summary(listings, {'snapshots': ['2026-06-15'], 'currency': 'CAD'})[0]
    assert result['supply'] == 2 and result['price_n'] == 1 and result['median_price'] == 100
    assert result['entire_home_share'] is None and result['multi_listing_host_share'] is None


def test_qa_headline_counts_rule_hits_not_unique_rows():
    title, _ = viz_qa.headline_rules({('2026-06-15', 'price_missing_final'): 1,
                                    ('2026-06-15', 'critical_field_missing'): 1}, {'2026-06-15': 1})
    assert '2 lượt vi phạm' in title and '200' not in title and '%' not in title


@pytest.mark.parametrize('dates', [['2026-6-15'], ['2026-06-15', '2025-09-11']])
def test_dates_canonical_and_chronological(case, dates):
    _, cfg, config = case
    cfg['snapshots'] = dates
    config.write_text(json.dumps(cfg))
    with pytest.raises(ValueError):
        load_config(config)


def test_tv5_real_runner_reads_all_hand_labels_from_config(case):
    root, cfg, config = case
    spec = importlib.util.spec_from_file_location('tv5_runner', ROOT / 'scripts/run_tv5.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run(config)
    assert len(result['tables']['reviews']) == 3
    assert result['tables']['evaluation'][0]['manual_n'] == 1
    assert not (root / 'data/processed/real/non_llm/tv5/llm_reviews.csv').exists()


def test_spatial_all_missing_price_still_renders_supply_and_na(case):
    from airbnb import viz_spatial, kpi
    root, cfg, _ = case
    snap = cfg['price_snapshot']
    listings = [{'snapshot_date': snap, 'listing_id': '123', 'host_id': '', 'price': None,
                 'analysis_area': 'A01', 'room_type': '', 'latitude': 43.65, 'longitude': -79.4,
                 'neighbourhood_cleansed': 'Demo West'}]
    geo = json.loads((root / cfg['paths']['raw'] / snap / 'neighbourhoods.geojson').read_text())
    tables = {'listings': listings, 'market_kpi': kpi.summarize(listings, cfg),
              'neighbourhood_kpi': kpi.neighbourhood_summary(listings, cfg), 'geojson': {snap: geo}}
    assert sum(r['supply'] for r in tables['neighbourhood_kpi']) == 1
    assert len(viz_spatial.render(tables, root / 'empty_price_figures', cfg)) == 3


def test_missing_cache_stops_before_download_or_publishing(case):
    root, _, config = case
    with patch.object(pipeline, 'download') as downloader, pytest.raises(RuntimeError, match='Chưa có cache'):
        pipeline.run(config)
    downloader.assert_not_called()
    assert not (root / 'data/processed').exists()
