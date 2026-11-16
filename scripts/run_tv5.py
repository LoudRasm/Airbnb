"""Run TV5 review/baseline/LLM/KPI/figure analysis independently; no other member modules required."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import baseline, evaluate, llm, review_kpi, reviews, viz_reviews
from airbnb.io import load_config, rows, write_csv
from airbnb.loading import read_assignment, snapshot_rows


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def load_tv5_labels(root: Path) -> list[dict]:
    packet_path = root / 'data/samples/labeling/tv5.json'
    if not packet_path.exists():
        return []
    packet = json.loads(packet_path.read_text(encoding='utf-8'))
    return [
        row for row in packet.get('labels', [])
        if row.get('sentiment') in llm.SENTIMENTS and not row.get('needs_review')
    ]


def load_manifest_records(root: Path) -> list[dict]:
    directory = root / 'data/samples/labeling'
    records = []
    for member in ('tv1', 'tv2', 'tv3', 'tv4', 'tv5'):
        p = directory / f'{member}.json'
        if p.exists():
            data = json.loads(p.read_text(encoding='utf-8'))
            records.extend(data.get('labels', []))
    return records


def run(config_path, demo=False, skip_llm=True):
    cfg, root = load_config(config_path)
    assignment = None
    stage = 'synthetic_demo' if demo else 'committed_packets_and_raw'

    if not demo:
        workbook_path = root / cfg['assignment']['path']
        if workbook_path.exists():
            assignment = read_assignment(cfg, root, demo=False)
            stage = 'assigned_workbook_raw'

    deduped_reviews = {}
    qa_rows = []

    if demo:
        for snapshot in cfg['snapshots']:
            issues = reviews.collect(
                snapshot_rows(root, cfg, snapshot, 'reviews.csv.gz', None, demo=True),
                snapshot,
                deduped_reviews,
            )
            for rule, affected in sorted(issues.items()):
                qa_rows.append({'snapshot_date': snapshot, 'table': 'reviews', 'rule': rule, 'affected_rows': affected})
        labels = list(rows(root / 'data/samples/demo_labels.csv'))
    elif assignment is not None:
        for snapshot in cfg['snapshots']:
            issues = reviews.collect(
                snapshot_rows(root, cfg, snapshot, 'reviews.csv.gz', assignment, demo=False),
                snapshot,
                deduped_reviews,
            )
            for rule, affected in sorted(issues.items()):
                qa_rows.append({'snapshot_date': snapshot, 'table': 'reviews', 'rule': rule, 'affected_rows': affected})
        manual_csv = root / cfg['paths']['manual_labels']
        labels = list(rows(manual_csv)) if manual_csv.exists() and list(rows(manual_csv)) else load_tv5_labels(root)
    else:
        manifest_rows = load_manifest_records(root)
        issues = reviews.collect(manifest_rows, cfg['snapshots'][-1], deduped_reviews)
        for rule, affected in sorted(issues.items()):
            qa_rows.append({'snapshot_date': cfg['snapshots'][-1], 'table': 'reviews', 'rule': rule, 'affected_rows': affected})
        labels = load_tv5_labels(root)

    review_list = sorted(deduped_reviews.values(), key=lambda r: int(r['review_id']))
    baseline_rows = [baseline.predict(r) for r in review_list]
    baseline_detailed = [baseline.predict_with_aspects(r, cfg['llm']['aspects']) for r in review_list]

    llm_rows = []
    if not skip_llm:
        target_ids = None if assignment is None else assignment.llm_ids
        llm_rows = llm.analyze(review_list, cfg, root, target_ids)

    active_preds = llm_rows if llm_rows else baseline_detailed
    eval_rows = []
    if labels:
        label_ids = {r['review_id'] for r in labels}
        if llm_rows:
            eval_rows.extend(evaluate.evaluate([r for r in llm_rows if r['review_id'] in label_ids], labels, 'llm'))
        eval_rows.extend(evaluate.evaluate([r for r in baseline_rows if r['review_id'] in label_ids], labels, 'baseline'))

    kpi_rows = review_kpi.guest_kpi(active_preds, [], cfg)
    cost_info = llm.estimate_cost(review_list, cfg)

    suffix = 'demo' if demo else 'real'
    processed = root / cfg['paths']['processed'] / suffix / 'tv5'
    reports_dir = root / cfg['paths']['reports'] / suffix / 'tv5'
    figures_dir = root / cfg['paths']['figures'] / suffix / 'tv5'

    write_csv(processed / 'reviews.csv', review_list, reviews.REVIEW_FIELDS)
    write_csv(processed / 'baseline.csv', baseline_rows, baseline.BASELINE_FIELDS)
    write_csv(processed / 'kpi_guest.csv', kpi_rows, review_kpi.GUEST_KPI_FIELDS)
    if eval_rows:
        write_csv(reports_dir / 'evaluation.csv', eval_rows, evaluate.EVALUATION_FIELDS)

    tables = {
        'reviews': review_list,
        'baseline': baseline_detailed,
        'llm_reviews': llm_rows,
        'evaluation': eval_rows,
        'guest_kpi': kpi_rows,
    }
    images = viz_reviews.render(tables, figures_dir, cfg)

    reports_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'analysis_version': 'tv5-reviews-v1',
        'demo': demo,
        'input_stage': stage,
        'reviews_n': len(review_list),
        'labels_n': len(labels),
        'cost_estimate': cost_info,
        'code_sha256': {
            name: digest(ROOT / name)
            for name in [
                'src/airbnb/reviews.py',
                'src/airbnb/baseline.py',
                'src/airbnb/llm.py',
                'src/airbnb/evaluate.py',
                'src/airbnb/review_kpi.py',
                'src/airbnb/viz_reviews.py',
            ]
        },
    }
    (reports_dir / 'run_metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'TV5 {suffix}: {len(review_list)} reviews, {len(kpi_rows)} KPI rows, {len(images)} figures')
    return {'tables': tables, 'processed': processed, 'reports': reports_dir, 'figures': images}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--demo', action='store_true', help='Run on synthetic demo fixture')
    parser.add_argument('--with-llm', action='store_true', help='Call Gemini API or cache for LLM predictions')
    args = parser.parse_args(argv)
    try:
        run(args.config, demo=args.demo, skip_llm=not args.with_llm)
        return 0
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f'TV5 analysis stopped: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
