"""Run TV1 cohort analysis independently; no member modules, downloads or API calls."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import analysis, viz_market
from airbnb.io import load_config, rows, write_csv
from airbnb.loading import read_assignment, snapshot_rows


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def demo_records(snapshots):
    """Synthetic, clearly scoped fixture; never used as evidence about Toronto."""
    return [{'snapshot_date': snapshot, 'listing_id': str(9001 + j),
             'host_id': str(101 + j + (100 if i and j == 0 else 0)),
             'room_type': 'Entire home/apt' if j < 2 else ('Private room' if i < 2 else 'Entire home/apt')}
            for i, snapshot in enumerate(snapshots) for j in range(3)]


def run(config_path, demo=False, listings_path=None):
    cfg, root = load_config(config_path)
    if demo and listings_path:
        raise ValueError('--demo cannot use real --listings input')
    assignment = read_assignment(cfg, root, demo)
    sources = []
    if demo:
        listings = demo_records(cfg['snapshots'])
        stage = 'synthetic_demo'
    elif listings_path:
        source = Path(listings_path).resolve()
        listings = list(rows(source))
        sources = [source]
        stage = 'provided_cleaned_listings'
    else:
        listings = []
        for snapshot in cfg['snapshots']:
            sources.append(root / cfg['paths']['raw'] / snapshot / 'listings.csv.gz')
            for row in snapshot_rows(root, cfg, snapshot, 'listings.csv.gz', assignment):
                # Identifier projection only. Listings cleaning/KPI remains TV2/TV3 work.
                listings.append({'snapshot_date': snapshot, 'listing_id': row['id'],
                                 'host_id': row['host_id'], 'room_type': row['room_type']})
        stage = 'assigned_raw_identifier_projection'
    cohort = analysis.cohort_summary(listings, cfg['snapshots'],
                                     None if assignment is None else assignment.listing_ids)
    transitions = analysis.churn(listings, cfg['snapshots'])
    tables = {'listings': listings, 'cohort_summary': cohort, 'churn_kpi': transitions}
    suffix = 'demo' if demo else 'real'
    processed = root / cfg['paths']['processed'] / suffix / 'tv1'
    reports = root / cfg['paths']['reports'] / suffix / 'tv1'
    figures = root / cfg['paths']['figures'] / suffix / 'tv1'
    metadata = {'generated_at_utc': datetime.now(timezone.utc).isoformat(),
                'analysis_version': 'tv1-cohort-v1', 'demo': demo, 'input_stage': stage,
                'scope': 'assigned_listing_cohort' if assignment else 'synthetic_observed_union',
                'data_code': assignment.code if assignment else 'DEMO',
                'stakeholder': cfg.get('stakeholder'), 'snapshots': cfg['snapshots'],
                'workbook_sha256': assignment.fingerprint if assignment else None,
                'config_sha256': digest(config_path),
                'source_files': [{'path': str(p.relative_to(root)) if p.is_relative_to(root) else str(p),
                                  'sha256': digest(p)} for p in sources],
                'code_sha256': {name: digest(ROOT / name) for name in
                               ['src/airbnb/analysis.py', 'src/airbnb/viz_market.py', 'scripts/run_tv1.py']},
                'python': sys.version,
                'limits': ['Not a Toronto market-entry/exit estimate',
                           'Changed host_id is not proof of a legal ownership change',
                           'Standalone raw projection does not replace the full QA pipeline']}
    write_csv(processed / 'kpi_cohort.csv', cohort, analysis.SUMMARY_FIELDS)
    write_csv(processed / 'kpi_cohort_transitions.csv', transitions, analysis.TRANSITION_FIELDS)
    images = viz_market.render(tables, figures, cfg)
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'run_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# TV1 — kết quả tái lập', '', f'Mã: {metadata["data_code"]}; input: {stage}.', '',
             '| Mốc | Quan sát / cohort | Host ID duy nhất hợp lệ |', '|---|---|---|']
    lines.extend(f'| {r["snapshot_date"]} | {r["observed_listings"]}/{r["cohort_size"]} | {r["observed_hosts"]} |' for r in cohort)
    lines.extend(['', '| Khoảng | Host ID đổi / so sánh được | Loại phòng đổi / so sánh được |', '|---|---|---|'])
    lines.extend(f'| {r["previous_snapshot"]} → {r["snapshot_date"]} | {r["host_changed"]}/{r["host_comparable"]} | '
                 f'{r["room_type_changed"]}/{r["room_type_comparable"]} |' for r in transitions)
    lines.extend(['', 'Chỉ mô tả các ID được giao. Không suy ra entry/exit toàn Toronto hoặc chuyển quyền sở hữu.',
                  'Nếu input là raw projection, đây chưa phải kết quả tích hợp sau QA toàn nhóm.', ''])
    (reports / 'summary.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'TV1 {suffix}: {len(cohort)} snapshots, {len(transitions)} transitions')
    print(f'CSV: {processed}\nFigures: {figures}\nMetadata/report: {reports}')
    return {'tables': tables, 'processed': processed, 'reports': reports, 'figures': images}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--demo', action='store_true', help='Synthetic fixture, no workbook/raw/API needed')
    parser.add_argument('--listings', type=Path, help='Optional cleaned CSV; default uses raw ID/host/room projection')
    args = parser.parse_args(argv)
    try:
        run(args.config, args.demo, args.listings)
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f'TV1 analysis stopped: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
