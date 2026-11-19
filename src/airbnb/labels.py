"""Read and validate hand labels without modifying the original files."""
from .io import rows
from . import llm


def manual_labels(root, assignment=None, demo=False, path=None):
    path = root / (path or ('data/samples/demo_labels.csv' if demo else 'data/samples/manual_labels.csv'))
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
