"""CLI entry point; orchestration lives in airbnb.pipeline."""
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from airbnb.pipeline import run, module_status


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
            state = 'READY' if row['ready'] else ('REVIEW' if row['implemented'] else 'TODO')
            extra = '' if row['required'] else ' (bỏ qua trong --skip-llm)'
            print(f'{state}: {row["module"]} — {row["owner"]}{extra}')
        return 0
    try:
        run(args.config, args.demo, args.skip_llm, args.no_download)
        return 0
    except (NotImplementedError, ValueError, OSError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
