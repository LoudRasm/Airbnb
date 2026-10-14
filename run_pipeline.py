"""TV1 orchestration. Member modules are imported here and implemented on their branches."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from airbnb.io import load_config, rows, write_csv
from airbnb.download import download, validate, FILES
from airbnb.loading import read_assignment, snapshot_rows
from airbnb import qa, eda, calendar, reviews, kpi, analysis, baseline, llm, evaluate, review_kpi
from airbnb import viz, viz_market, viz_qa, viz_spatial, viz_calendar, viz_reviews

CORE_MODULES = (qa, eda, calendar, reviews, kpi, analysis, baseline,
                viz_market, viz_qa, viz_spatial, viz_calendar)
LLM_MODULES = (llm, evaluate, review_kpi, viz_reviews)


def module_status(skip_llm=False):
    required = CORE_MODULES + (() if skip_llm else LLM_MODULES)
    return [{'module': module.__name__, 'owner': module.OWNER,
             'ready': module.READY, 'required': module in required}
            for module in CORE_MODULES + LLM_MODULES]


def require_implemented(skip_llm=False):
    pending = [r for r in module_status(skip_llm) if r['required'] and not r['ready']]
    if pending:
        details = '\n'.join(f'- {r["module"]}: {r["owner"]}' for r in pending)
        raise NotImplementedError('Pipeline phân tích còn TODO, chưa tải dữ liệu hoặc tạo kết quả:\n' + details)


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


def manual_labels(root, assignment=None, demo=False):
    path = root / ('data/samples/demo_labels.csv' if demo else 'data/samples/manual_labels.csv')
    labels = list(rows(path))
    seen = set()
    for row in labels:
        identity = row.get('review_id', '')
        if not identity or identity in seen or row.get('sentiment') not in llm.SENTIMENTS:
            raise ValueError('Manual labels need unique review_id and positive/mixed/negative sentiment')
        seen.add(identity)
    if assignment is not None and not assignment.manual_ids <= seen:
        raise ValueError('Missing the 100 assigned hand-labelled reviews; x markers are not sentiment labels')
    return [r for r in labels if assignment is None or r['review_id'] in assignment.manual_ids]


def run(config_path, demo=False, skip_llm=False, no_download=False):
    cfg, root = load_config(config_path)
    require_implemented(skip_llm)  # Fail before network calls, reading raw, or writing results.
    if demo and not skip_llm:
        raise ValueError('Demo requires --skip-llm; do not send synthetic review data to the API')
    assignment = read_assignment(cfg, root, demo)
    labels = [] if skip_llm else manual_labels(root, assignment, demo)
    if not demo and not no_download:
        download(cfg, root)
    listings, calendars, qa_report, review_map = [], [], [], {}
    for snapshot in cfg['snapshots']:
        folder = root / ('data/samples/demo' if demo else cfg['paths']['raw']) / snapshot
        for name, (_, required) in FILES.items():
            validate(folder / name, required)
        cleaned, report = qa.clean_listings(snapshot_rows(root, cfg, snapshot, 'listings.csv.gz', assignment, demo), snapshot, cfg)
        listings.extend(cleaned)
        qa_report.extend(report)
        cal, issues = calendar.aggregate(snapshot_rows(root, cfg, snapshot, 'calendar.csv.gz', assignment, demo),
                                         snapshot, cfg['calendar']['window_days'], {r['listing_id'] for r in cleaned})
        calendars.extend(cal)
        issues.update(reviews.collect(snapshot_rows(root, cfg, snapshot, 'reviews.csv.gz', assignment, demo), snapshot, review_map))
        qa_report.extend({'snapshot_date': snapshot, 'rule': rule, 'affected_rows': count,
                          'action': 'owner_defined', 'rows_after': '', 'median_price_before': '', 'median_price_after': ''}
                         for rule, count in issues.items())
    tables = {'listings': listings, 'calendar': calendars, 'reviews': list(review_map.values()),
              'qa_report': qa_report, 'eda': eda.profile(listings),
              'market_kpi': kpi.summarize(listings, cfg),
              'calendar_kpi': calendar.metrics(calendars, listings, cfg),
              'churn_kpi': analysis.churn(listings, cfg['snapshots']),
              'baseline': [baseline.predict(r) for r in review_map.values()],
              'llm_reviews': [], 'guest_kpi': [], 'evaluation': []}
    if not skip_llm:
        tables['llm_reviews'] = llm.analyze(tables['reviews'], cfg, root, assignment.llm_ids)
        tables['guest_kpi'] = review_kpi.guest_kpi(tables['llm_reviews'], listings, cfg)
        paired = {r['review_id'] for r in tables['llm_reviews']}
        tables['evaluation'] = evaluate.evaluate([r for r in tables['baseline'] if r['review_id'] in paired], labels, 'baseline') + evaluate.evaluate(tables['llm_reviews'], labels, 'llm')
    suffix = 'demo' if demo else 'real'
    processed = root / cfg['paths']['processed'] / suffix
    reports = root / cfg['paths']['reports'] / suffix
    figures = root / cfg['paths']['figures'] / suffix
    outputs = [
        (processed / 'listings.csv', 'listings', ['snapshot_date','listing_id','host_id','price','room_type','analysis_area','neighbourhood_cleansed','latitude','longitude','qa_flags']),
        (processed / 'calendar_summary.csv', 'calendar', ['snapshot_date','listing_id','available_days','observed_days','expected_days','availability_rate']),
        (processed / 'reviews.csv', 'reviews', ['review_id','listing_id','date','comments','first_seen_snapshot']),
        (processed / 'kpi_market.csv', 'market_kpi', ['snapshot_date','analysis_area','supply','median_price','price_n','currency','entire_home_share','multi_listing_host_share']),
        (processed / 'kpi_calendar.csv', 'calendar_kpi', ['snapshot_date','analysis_area','availability_rate','observed_days','expected_days','listing_n']),
        (processed / 'kpi_churn.csv', 'churn_kpi', ['previous_snapshot','snapshot_date','new','retained','disappeared','entry_rate','exit_rate']),
        (processed / 'baseline.csv', 'baseline', ['review_id','sentiment','source']),
        (processed / 'llm_reviews.csv', 'llm_reviews', ['review_id','sentiment','language','positive_aspects','negative_aspects','source']),
        (processed / 'kpi_guest.csv', 'guest_kpi', ['metric','value','sample_n','source','scope']),
        (reports / 'qa_report.csv', 'qa_report', ['snapshot_date','rule','affected_rows','action','rows_after','median_price_before','median_price_after']),
        (reports / 'eda_flags.csv', 'eda', ['snapshot_date','qa_flags','count']),
        (reports / 'evaluation.csv', 'evaluation', ['source','paired_n','manual_n','accuracy','macro_f1','meets_100_paired']),
    ]
    # First validate the complete result set; missing columns do not leave a half-written run.
    for path, key, fields in outputs:
        for row in tables[key]:
            if set(fields) - row.keys():
                raise ValueError(f'{key}: missing columns {sorted(set(fields)-row.keys())}')
    for path, key, fields in outputs:
        records_csv(path, tables[key], fields)
    if not demo:
        records_csv(root / 'reports/qa_report.csv', tables['qa_report'], outputs[9][2])
    figures.mkdir(parents=True, exist_ok=True)
    viz.render_all(tables, figures, cfg, skip_llm)
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'run_metadata.json').write_text(json.dumps({'demo': demo, 'llm_status': 'skipped' if skip_llm else 'owner_implemented',
        'config': cfg, 'python': sys.version}, indent=2) + '\n', encoding='utf-8')
    print(f'Completed {suffix}; outputs: {processed}, {reports}, {figures}')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--status', action='store_true', help='Show owner/module TODO status without running data or APIs')
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--skip-llm', action='store_true')
    parser.add_argument('--no-download', action='store_true')
    args = parser.parse_args(argv)
    if args.status:
        for row in module_status(args.skip_llm):
            state = 'READY' if row['ready'] else 'TODO'
            extra = '' if row['required'] else ' (bỏ qua trong --skip-llm)'
            print(f'{state}: {row["module"]} — {row["owner"]}{extra}')
        return 0
    try:
        run(args.config, args.demo, args.skip_llm, args.no_download)
        return 0
    except (NotImplementedError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
