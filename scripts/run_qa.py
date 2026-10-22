"""Chạy QA listings (TV2) trên đúng ID của nhóm theo config/workbook và xuất kết quả.

Lệnh: python scripts/run_qa.py --config configs/toronto.yaml
Đọc : data/raw/<mốc>/listings.csv.gz (+ neighbourhoods.geojson nếu có) và workbook theo config;
      không sửa, không tải.
Ghi : reports/data_dictionary.csv, reports/qa_rule_catalog.csv (tĩnh, commit được) và
      reports/generated/real/ (gitignore): qa_report_listings.csv, qa_kpi_impact.csv,
      qa_missingness.csv.
Pipeline chung dùng cùng các hàm trong src/airbnb/qa.py; script này chỉ để tái lập/kiểm chứng.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import qa
from airbnb.io import load_config, write_csv
from airbnb.loading import read_assignment, snapshot_rows

REPORT_FIELDS = ['snapshot_date', 'rule', 'affected_rows', 'action', 'rows_after',
                 'median_price_before', 'median_price_after']


def read_names(path):
    """Tên neighbourhood từ geojson của mốc; None nếu mốc chưa có file."""
    if not path.exists():
        return None
    return qa.neighbourhood_names(json.loads(path.read_text(encoding='utf-8')))


def run(config_path, out_dir=None):
    cfg, root = load_config(config_path)
    assignment = read_assignment(cfg, root)
    generated = Path(out_dir) if out_dir else root / cfg['paths']['reports'] / 'real'
    static = Path(out_dir) if out_dir else root / 'reports'
    raw_by_snapshot, names, no_geojson = {}, {}, []
    for snapshot in cfg['snapshots']:
        raw_by_snapshot[snapshot] = list(snapshot_rows(root, cfg, snapshot, 'listings.csv.gz', assignment))
        found = read_names(root / cfg['paths']['raw'] / snapshot / 'neighbourhoods.geojson')
        if found is None:
            no_geojson.append(snapshot)
        else:
            names[snapshot] = found
    result = qa.run_listings_qa(raw_by_snapshot, cfg, names)
    write_csv(generated / 'qa_report_listings.csv', result['qa_report'], REPORT_FIELDS)
    write_csv(generated / 'qa_kpi_impact.csv', result['kpi_impact'],
              ['snapshot_date', 'kpi', 'before', 'after', 'delta'])
    write_csv(generated / 'qa_missingness.csv', result['missingness'],
              ['snapshot_date', 'column', 'column_present', 'rows', 'missing', 'missing_rate'])
    write_csv(static / 'data_dictionary.csv', qa.data_dictionary(),
              ['column', 'type', 'description', 'source', 'qa_rules'])
    write_csv(static / 'qa_rule_catalog.csv', qa.rule_catalog(),
              ['rule', 'group', 'condition', 'reason', 'action'])
    return generated, static, result, no_geojson


def main(argv=None):
    parser = argparse.ArgumentParser(description='QA listings theo workbook của nhóm')
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--out', help='Một thư mục xuất chung cho mọi file (mặc định: reports/ và reports/generated/real)')
    args = parser.parse_args(argv)
    try:
        generated, static, result, no_geojson = run(args.config, args.out)
    except (OSError, ValueError, KeyError) as exc:
        print(f'Cannot run QA: {exc}', file=sys.stderr)
        return 2
    print(f'QA listings: {len(result["cleaned"])} cleaned rows, {len(result["qa_report"])} report rows')
    print(f'Generated: {generated}; static docs: {static}')
    if no_geojson:
        print(f'No neighbourhoods.geojson for {", ".join(no_geojson)}; reference check skipped there.', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
