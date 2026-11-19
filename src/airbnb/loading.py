"""TV1: dữ liệu đầu vào dùng chung, không chứa QA/KPI/NLP của các thành viên."""
import json
from .assignment import Assignment, load_assignment
from .io import rows


def read_assignment(cfg, root, demo=False):
    if demo:
        return None
    options = cfg['assignment']
    workbook = root / options['path']
    if workbook.exists():
        assigned = load_assignment(workbook, options['course_class'], options['group'])
    else:
        data = json.loads((root / options['manifest']).read_text(encoding='utf-8'))
        for key in ('listing_ids', 'review_ids', 'llm_ids', 'manual_ids'):
            values = data[key]
            if any(not isinstance(v, str) or not v.isascii() or not v.isdigit() for v in values) or len(set(values)) != len(values):
                raise ValueError('Assignment manifest needs unique string IDs')
            data[key] = set(values)
        assigned = Assignment(**data)
    if (assigned.code != options['data_code'] or assigned.course_class != options['course_class']
            or assigned.group != options['group'] or assigned.city.casefold() != cfg['city'].casefold()):
        raise ValueError('Config identity must match the lecturer assignment')
    if not assigned.manual_ids <= assigned.llm_ids <= assigned.review_ids or set(assigned.areas) != assigned.listing_ids:
        raise ValueError('Invalid assignment ID sets')
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
