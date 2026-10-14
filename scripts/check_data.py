"""Run one member's checks, or merge the team's CSVs into the submission."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb.data_check import PARTS, context, run_part, merge


def main(argv=None):
    parser = argparse.ArgumentParser(description='Workbook → assigned raw data → per-member CSV → group report')
    parser.add_argument('--part', required=True, choices=[*PARTS, 'merge', 'all'])
    parser.add_argument('--config', default=str(ROOT / 'configs/data_check.json'))
    parser.add_argument('--assignment', help='Path to lecturer XLSX; otherwise data/assignments/assignment.xlsx')
    args = parser.parse_args(argv)
    try:
        root, cfg, assignment = context(args.config, args.assignment)
        print(f'Group: {assignment.course_class} - {assignment.group}; code: {assignment.code}', flush=True)
        print(f'Snapshots: {", ".join(assignment.snapshots)}', flush=True)
        if args.part == 'all':
            for part in PARTS:
                run_part(root, cfg, assignment, part)
            ok = merge(root, cfg, assignment)
        elif args.part == 'merge':
            ok = merge(root, cfg, assignment)
        else:
            ok = run_part(root, cfg, assignment, args.part)
        if not ok:
            print('Checks incomplete or mismatched. Read the generated notes; do not submit the draft.', file=sys.stderr)
        return 0 if ok else 1
    except (OSError, ValueError, KeyError) as exc:
        print(f'Cannot start checks: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
