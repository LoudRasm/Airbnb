"""TV1: dữ liệu đầu vào dùng chung, không chứa QA/KPI/NLP của các thành viên."""
from .assignment import load_assignment
from .io import rows


def read_assignment(cfg, root, demo=False):
    if demo:
        return None
    options = cfg['assignment']
    assigned = load_assignment(root / options['path'], options['course_class'], options['group'])
    if assigned.code != options['data_code'] or assigned.snapshots != cfg['snapshots']:
        raise ValueError('Config code/snapshots must match the lecturer workbook')
    if assigned.currency != cfg['currency']:
        raise ValueError('Config currency must match the workbook')
    return assigned


def snapshot_rows(root, cfg, snapshot, name, assignment=None, demo=False):
    """Streaming raw rows: assigned listings/calendar IDs or independent review IDs."""
    folder = root / ('data/samples/demo' if demo else cfg['paths']['raw']) / snapshot
    if assignment is None:
        yield from rows(folder / name)
        return
    assigned_ids = assignment.review_ids if name == 'reviews.csv.gz' else assignment.listing_ids
    key = 'listing_id' if name == 'calendar.csv.gz' else 'id'
    for row in rows(folder / name):
        identity = row.get(key, '').strip()
        if identity not in assigned_ids:
            continue
        if name == 'listings.csv.gz':
            row = {**row, 'analysis_area': assignment.areas[identity]}
        yield row
