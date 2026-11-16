"""Explicit, resumable Gemini generation. Grading never invokes this script."""
import argparse
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb import llm, reviews
from airbnb.io import load_config
from airbnb.loading import read_assignment, snapshot_rows


def _load_env_if_present(root: Path):
    """Nạp GEMINI_API_KEY từ file .env nếu có và môi trường chưa thiết lập."""
    if os.environ.get('GEMINI_API_KEY'):
        return
    env_file = root / '.env'
    if env_file.is_file():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith('GEMINI_API_KEY=') and not line.startswith('#'):
                val = line.split('=', 1)[1].strip().strip('"\'')
                if val:
                    os.environ['GEMINI_API_KEY'] = val
                    break


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--check', action='store_true', help='Validate completeness without an API/key or writing cache')
    args = parser.parse_args(argv)
    try:
        cfg, root = load_config(args.config)
        _load_env_if_present(root)
        assignment = read_assignment(cfg, root)
        if not set(assignment.snapshots) <= set(cfg['snapshots']):
            raise ValueError('Cache generation requires all four assigned snapshots')
        collected = {}
        for snap in cfg['snapshots']:
            reviews.collect(snapshot_rows(root, cfg, snap, 'reviews.csv.gz', assignment), snap, collected)
        result = llm.analyze(list(collected.values()), cfg, root, assignment.llm_ids, allow_api=not args.check)
        print(f'Validated {len(result)} assigned predictions: {root / cfg["llm"]["cache"]}')
        return 0
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
