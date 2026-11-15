"""Prepare human annotation packets; validate and merge them without importing the pipeline.

No labels are predicted. All IDs come from the lecturer workbook's manual-label subset.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from airbnb.assignment import load_assignment
from airbnb.io import load_config, rows

TEAM = {
    'tv1': 'Dương Nhật Huy',
    'tv2': 'Mai Anh Đức',
    'tv3': 'Nguyễn Quốc Hiếu',
    'tv4': 'Vũ Phạm Khánh Nam',
    'tv5': 'Phan Ngọc Huy',
}
SENTIMENTS = {'positive', 'mixed', 'negative'}
TEXT_FIELDS = ('review_id', 'listing_id', 'date', 'comments')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def text_hash(row):
    payload = json.dumps({key: row[key] for key in TEXT_FIELDS}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def configured_assignment(config):
    cfg, root = load_config(config)
    options = cfg['assignment']
    assignment = load_assignment(root / options['path'], options['course_class'], options['group'])
    if (assignment.code != options['data_code'] or assignment.snapshots != cfg['snapshots']
            or assignment.currency != cfg['currency']):
        raise ValueError('Config does not match the lecturer workbook')
    if (len(assignment.review_ids), len(assignment.llm_ids), len(assignment.manual_ids)) != (5000, 1000, 100):
        raise ValueError('Group packets require the assigned 5000/1000/100 review sets')
    return cfg, root, assignment


def extract_reviews(source, manual_ids):
    found = {}
    for row in rows(source):
        identity = row.get('id', '').strip()
        if identity not in manual_ids:
            continue
        if identity in found:
            raise ValueError(f'Duplicate assigned review in raw: {identity}')
        if not row.get('comments', '').strip():
            raise ValueError(f'Assigned review has no text; do not replace its ID: {identity}')
        found[identity] = {'review_id': identity, 'listing_id': row['listing_id'],
                           'date': row['date'], 'comments': row['comments']}
    absent = manual_ids - found.keys()
    if absent:
        raise ValueError(f'Assigned review IDs not found: {sorted(absent)}')
    return found


def prepare(assignment, source, directory):
    directory = Path(directory)
    planned = [directory / 'manifest.json', *[directory / f'{member}.json' for member in TEAM]]
    if any(path.exists() for path in planned):
        raise ValueError('Packets already exist; use the committed files, never overwrite human work')
    if len(assignment.manual_ids) != 100 or not assignment.manual_ids <= assignment.llm_ids <= assignment.review_ids:
        raise ValueError('Need exactly 100 manual IDs inside the assigned LLM/review sets')
    found = extract_reviews(source, assignment.manual_ids)
    ordered = sorted(assignment.manual_ids, key=int)  # Integer sort preserves long IDs exactly.
    manifest = {'format_version': 1, 'guideline_version': '1.0',
                'data_code': assignment.code, 'workbook_sha256': assignment.fingerprint,
                'source_snapshot': assignment.snapshots[-1], 'source_sha256': file_hash(source),
                'source_file': f'data/raw/{assignment.snapshots[-1]}/reviews.csv.gz',
                'selection': 'Workbook Review / Nhãn tay = x; no extra listing_id filter',
                'members': {}, 'text_sha256': {identity: text_hash(found[identity]) for identity in ordered}}
    packets = {}
    for index, (member, name) in enumerate(TEAM.items()):
        identities = ordered[index * 20:(index + 1) * 20]
        manifest['members'][member] = {'name': name, 'review_ids': identities}
        packets[member] = {'data_code': assignment.code, 'member': member,
                           'guideline_version': manifest['guideline_version'],
                           'source_snapshot': manifest['source_snapshot'],
                           'labels': [{**found[identity], 'sentiment': '', 'needs_review': False, 'note': ''}
                                      for identity in identities]}
    directory.mkdir(parents=True, exist_ok=True)
    for member, packet in packets.items():
        save_json(directory / f'{member}.json', packet)
    save_json(directory / 'manifest.json', manifest)
    return manifest


def validate_manifest(manifest):
    if manifest.get('format_version') != 1 or set(manifest['members']) != set(TEAM):
        raise ValueError('Unsupported packet manifest or wrong members')
    identities = []
    for member in TEAM:
        group = manifest['members'][member]['review_ids']
        if len(group) != 20 or any(not isinstance(key, str) or not key.isascii() or not key.isdigit() for key in group):
            raise ValueError(f'{member}: need 20 exact string IDs')
        identities.extend(group)
    if len(set(identities)) != 100 or set(identities) != set(manifest['text_sha256']):
        raise ValueError('Manifest IDs are duplicated, missing or outside the frozen text set')


def inspect_packet(packet, manifest, member):
    for key, expected in [('data_code', manifest['data_code']), ('member', member),
                          ('guideline_version', manifest['guideline_version']),
                          ('source_snapshot', manifest['source_snapshot'])]:
        if packet.get(key) != expected:
            raise ValueError(f'{member}: wrong {key}')
    records = packet['labels']
    expected = set(manifest['members'][member]['review_ids'])
    identities = [row['review_id'] for row in records]
    if any(not isinstance(key, str) for key in identities):
        raise ValueError(f'{member}: review_id must stay a string in quotes')
    if len(identities) != 20 or len(set(identities)) != 20 or set(identities) != expected:
        raise ValueError(f'{member}: changed, duplicate, missing or unassigned IDs')
    issues, labels = [], []
    for row in records:
        identity = row['review_id']
        if any(not isinstance(row[key], str) for key in TEXT_FIELDS):
            raise ValueError(f'{member}/{identity}: source fields must be text')
        if text_hash(row) != manifest['text_sha256'][identity]:
            raise ValueError(f'{member}/{identity}: source text/metadata changed; restore it')
        sentiment = row.get('sentiment')
        uncertain = row.get('needs_review')
        note = row.get('note')
        if not isinstance(note, str) or type(uncertain) is not bool:
            raise ValueError(f'{member}/{identity}: note must be text and needs_review true/false')
        if not isinstance(sentiment, str) or sentiment not in SENTIMENTS:
            issues.append(f'{member}/{identity}: sentiment blank or outside positive/mixed/negative')
        if uncertain:
            issues.append(f'{member}/{identity}: needs human adjudication before merge')
        labels.append({'review_id': identity, 'sentiment': sentiment})
    return labels, issues


def check(directory, member=None):
    directory = Path(directory)
    manifest = read_json(directory / 'manifest.json')
    validate_manifest(manifest)
    labels, issues = [], []
    for owner in ([member] if member else TEAM):
        selected, errors = inspect_packet(read_json(directory / f'{owner}.json'), manifest, owner)
        labels.extend(selected)
        issues.extend(errors)
    return manifest, labels, issues


def merge(directory, assignment, source, output):
    manifest, labels, issues = check(directory)
    if issues:
        raise ValueError(f'{len(issues)} unresolved annotation checks; first: {issues[0]}')
    if (manifest['data_code'] != assignment.code or manifest['workbook_sha256'] != assignment.fingerprint
            or manifest['source_snapshot'] != assignment.snapshots[-1]
            or {row['review_id'] for row in labels} != assignment.manual_ids):
        raise ValueError('Packets no longer match this workbook; review provenance before merging')
    if manifest['source_sha256'] != file_hash(source):
        raise ValueError('Raw source changed; review text versions before merging')
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=['review_id', 'sentiment'], lineterminator='\n')
    writer.writeheader()
    writer.writerows(sorted(labels, key=lambda row: int(row['review_id'])))
    content = buffer.getvalue()
    output = Path(output)
    if output.exists() and list(rows(output)) and output.read_text(encoding='utf-8') != content:
        raise ValueError('Output already contains different labels; use --output for a candidate and review the diff')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + '.tmp')
    try:
        temporary.write_text(content, encoding='utf-8', newline='')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return len(labels)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(ROOT / 'configs/toronto.yaml'))
    parser.add_argument('--directory', type=Path, default=ROOT / 'data/samples/labeling')
    actions = parser.add_subparsers(dest='action', required=True)
    actions.add_parser('prepare', help='TV1/TV5 only: create 5 blank packets once')
    validate = actions.add_parser('check', help='Validate one packet, or all packets; no raw/workbook needed')
    validate.add_argument('--member', choices=TEAM)
    collect = actions.add_parser('merge', help='TV5/TV1 only: write the final 100 human labels')
    collect.add_argument('--output', type=Path, default=ROOT / 'data/samples/manual_labels.csv')
    args = parser.parse_args(argv)
    try:
        if args.action == 'check':
            _, labels, issues = check(args.directory, args.member)
            print(f'Checked {len(labels)} reviews; unresolved checks: {len(issues)}')
            for issue in issues:
                print(issue)
            return 1 if issues else 0
        cfg, root, assignment = configured_assignment(args.config)
        source = root / cfg['paths']['raw'] / assignment.snapshots[-1] / 'reviews.csv.gz'
        if args.action == 'prepare':
            prepare(assignment, source, args.directory)
            print(f'Created 5 x 20 blank human-label packets: {args.directory}')
        else:
            count = merge(args.directory, assignment, source, args.output)
            print(f'Saved {count} human labels: {args.output}')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Annotation step stopped: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
