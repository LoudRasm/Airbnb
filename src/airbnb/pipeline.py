"""Shared integration: load → member modules → validate → publish CSVs and figures."""
import hashlib
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from datetime import datetime, timezone
from .io import load_config, write_csv
from .download import download, validate, FILES
from .loading import read_assignment, snapshot_rows
from .labels import manual_labels
from .outputs import csv_outputs
from . import calendar, qa, eda, reviews, kpi, analysis, baseline, llm, evaluate, review_kpi
from . import viz, viz_market, viz_qa, viz_spatial, viz_calendar, viz_reviews

CORE_MODULES = (qa, eda, calendar, reviews, kpi, analysis, baseline,
                viz_market, viz_qa, viz_spatial, viz_calendar)
LLM_MODULES = (llm, evaluate, review_kpi, viz_reviews)


def module_status(skip_llm=False):
    required = CORE_MODULES + (() if skip_llm else LLM_MODULES)
    return [{'module': module.__name__, 'owner': module.OWNER,
             'ready': module.READY, 'implemented': getattr(module, 'IMPLEMENTED', module.READY),
             'required': module in required}
            for module in CORE_MODULES + LLM_MODULES]


def require_implemented(skip_llm=False):
    pending = [r for r in module_status(skip_llm) if r['required'] and not r['ready']]
    if pending:
        details = '\n'.join(f'- {r["module"]}: {r["owner"]}' for r in pending)
        raise NotImplementedError('Pipeline còn module chưa READY (TODO hoặc chờ review), chưa tải dữ liệu hoặc tạo kết quả:\n' + details)


def records_csv(path, records, fields):
    # Validate an owner's result before the shared writer persists it.
    records = list(records)
    for record in records:
        absent = set(fields) - record.keys()
        if absent:
            raise ValueError(f'{path.name}: member result missing columns {sorted(absent)}')
    selected = [{key: json.dumps(row[key], ensure_ascii=False) if isinstance(row[key], list) else row[key]
                 for key in fields} for row in records]
    write_csv(path, selected, fields)



def run(config_path, demo=False, skip_llm=False, no_download=False):
    cfg, root = load_config(config_path)
    require_implemented(skip_llm)
    if demo and not skip_llm:
        raise ValueError('Demo requires --skip-llm; synthetic data never goes to an API')
    assignment = read_assignment(cfg, root, demo)
    if not skip_llm and assignment and not set(assignment.snapshots) <= set(cfg['snapshots']):
        raise ValueError('Full evaluation requires all four assigned snapshots; use --skip-llm for an extra snapshot')
    label_path = cfg['paths'].get('manual_labels', 'data/samples/manual_labels.csv')
    labels = [] if skip_llm else manual_labels(root, assignment, demo, label_path)
    if not skip_llm and not (root / cfg['llm']['cache']).is_file():
        raise RuntimeError('Chưa có cache Gemini thật. Chạy scripts/generate_llm_cache.py rồi commit cache; pipeline không gọi API.')
    if not demo and not no_download:
        download(cfg, root)
    raw_by_snapshot, geojson = {}, {}
    inputs = []
    for snapshot in cfg['snapshots']:
        folder = root / ('data/samples/demo' if demo else cfg['paths']['raw']) / snapshot
        for name, (_, required) in FILES.items():
            path = folder / name
            validate(path, required)
            inputs.append(path)
        geojson[snapshot] = json.loads((folder / 'neighbourhoods.geojson').read_text(encoding='utf-8'))
        raw_by_snapshot[snapshot] = list(snapshot_rows(root, cfg, snapshot, 'listings.csv.gz', assignment, demo))
    names = {snap: qa.neighbourhood_names(value) for snap, value in geojson.items()}
    qa_result = qa.run_listings_qa(raw_by_snapshot, cfg, names)
    listings, qa_report = qa_result['cleaned'], qa_result['qa_report']
    calendars, review_map = [], {}
    for snapshot in cfg['snapshots']:
        print(f'Processing {snapshot}', flush=True)
        # Exposure is the entire assigned cohort, even if a listing was missing/dropped in QA.
        ids = assignment.listing_ids if assignment else {r.get('id', '') for r in raw_by_snapshot[snapshot]}
        cal, issues = calendar.aggregate(snapshot_rows(root, cfg, snapshot, 'calendar.csv.gz', assignment, demo),
                                         snapshot, cfg['calendar']['window_days'], ids)
        calendars.extend(cal)
        issues.update(reviews.collect(snapshot_rows(root, cfg, snapshot, 'reviews.csv.gz', assignment, demo), snapshot, review_map))
        qa_report.extend({'snapshot_date': snapshot, 'rule': rule, 'affected_rows': count,
                          'action': 'calendar_exclude_invalid_keep_missing_exposure' if 'calendar' in rule or 'available' in rule else 'review_keep_one_valid_id',
                          'rows_after': '', 'median_price_before': '', 'median_price_after': ''}
                         for rule, count in sorted(issues.items()))
    # Price is unavailable for analysis before the assigned last date, regardless of raw presence.
    price_snapshot = cfg.get('price_snapshot', cfg['snapshots'][-1])
    qa_report = [{**r, 'median_price_before': None, 'median_price_after': None}
                 if r['snapshot_date'] != price_snapshot else r for r in qa_report]
    qa_result['kpi_impact'] = [{**r, 'before': None, 'after': None, 'delta': None}
                             if r['snapshot_date'] != price_snapshot and r['kpi'] in {'median_price', 'price_n'} else r
                             for r in qa_result['kpi_impact']]
    listings = [{**r, 'price': r['price'] if r['snapshot_date'] == price_snapshot else None} for r in listings]
    exposure_listings = listings
    if assignment:
        seen = {(r['snapshot_date'], r['listing_id']) for r in listings}
        exposure_listings = listings + [{'snapshot_date': snap, 'listing_id': lid, 'analysis_area': area}
                                       for snap in cfg['snapshots'] for lid, area in assignment.areas.items()
                                       if (snap, lid) not in seen]
    tables = {'listings': listings, 'calendar': calendars, 'reviews': list(review_map.values()),
              'geojson': geojson, 'qa_report': qa_report, 'eda': eda.profile(listings),
              'missingness': qa_result['missingness'], 'kpi_impact': qa_result['kpi_impact'],
              'market_kpi': kpi.summarize(listings, cfg),
              'neighbourhood_kpi': kpi.neighbourhood_summary(listings, cfg),
              'calendar_kpi': calendar.metrics(calendars, exposure_listings, cfg),
              'cohort_summary': analysis.cohort_summary(listings, cfg['snapshots'], assignment.listing_ids if assignment else None),
              'churn_kpi': analysis.churn(listings, cfg['snapshots']),
              'baseline': [baseline.predict(r) for r in review_map.values()],
              'llm_reviews': [], 'guest_kpi': [], 'evaluation': []}
    if not skip_llm:
        predictions = llm.analyze(tables['reviews'], cfg, root, assignment.llm_ids if assignment else None)
        tables['llm_reviews'] = predictions
        # Join source listing_id; never ask the model to invent IDs or filter reviews by listing cohort.
        linked = [{**p, 'listing_id': review_map[p['review_id']]['listing_id']} for p in predictions]
        tables['guest_kpi'] = review_kpi.guest_kpi(linked, listings, cfg)
        selected = {r['review_id'] for r in predictions}
        tables['evaluation'] = evaluate.evaluate([r for r in tables['baseline'] if r['review_id'] in selected], labels, 'baseline') + evaluate.evaluate(predictions, labels, 'llm')
    suffix = 'demo' if demo else ('real/non_llm' if skip_llm else 'real')
    processed = root / cfg['paths']['processed'] / suffix
    reports = root / cfg['paths']['reports'] / suffix
    figures = root / cfg['paths']['figures'] / suffix
    previous_metadata = reports / 'run_metadata.json'
    previous_artifacts = set(json.loads(previous_metadata.read_text(encoding='utf-8')).get('artifacts', [])) if previous_metadata.exists() else set()
    # Validate and render into staging. A failed module/cache/schema does not publish partial new results.
    with TemporaryDirectory(prefix='airbnb-run-') as temporary:
        stage = Path(temporary)
        outputs = csv_outputs(stage / 'processed', stage / 'reports', skip_llm)
        for path, key, fields in outputs:
            records_csv(path, tables[key], fields)
        (stage / 'figures').mkdir(parents=True)
        viz.render_all(tables, stage / 'figures', cfg, skip_llm)
        artifact_paths = []
        for name, target in [('processed', processed), ('reports', reports), ('figures', figures)]:
            for path in (stage / name).rglob('*'):
                if path.is_file():
                    dest = target / path.relative_to(stage / name)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    # Same-directory temporary file makes replacement atomic per artifact.
                    part = dest.with_name(dest.name + '.tmp')
                    part.write_bytes(path.read_bytes())
                    os.replace(part, dest)
                    artifact_paths.append(str(dest.relative_to(root)))
    # Retire artifacts from this same mode that a config change no longer generates.
    # Only paths listed by our previous run and inside the three managed targets qualify.
    for name in previous_artifacts - set(artifact_paths):
        obsolete = (root / name).resolve()
        if any(obsolete.is_relative_to(target.resolve()) for target in (processed, reports, figures)) and obsolete.is_file():
            obsolete.unlink()
    def digest(path):
        h = hashlib.sha256()
        with Path(path).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        return h.hexdigest()
    metadata = {'generated_at_utc': datetime.now(timezone.utc).isoformat(), 'demo': demo,
                'llm_status': 'skipped_separate_output' if skip_llm else 'validated_cache_only',
                'assignment_sha256': assignment.fingerprint if assignment else None,
                'manual_labels_sha256': digest(root / label_path) if not skip_llm else None,
                'config': cfg, 'python': sys.version,
                'inputs': {str(p): digest(p) for p in inputs},
                'row_counts': {key: len(value) for key, value in tables.items() if isinstance(value, list)},
                'artifacts': artifact_paths}
    if not skip_llm:
        metadata['llm_cache_sha256'] = digest(root / cfg['llm']['cache'])
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'run_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if not demo:
        records_csv(root / 'reports/qa_report.csv', qa_report,
                    ['snapshot_date','rule','affected_rows','action','rows_after','median_price_before','median_price_after'])
    print(f'Completed {suffix}; outputs: {processed}, {reports}, {figures}')
    return tables
