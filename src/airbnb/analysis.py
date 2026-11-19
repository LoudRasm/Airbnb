"""TV1: coverage and reported attribute changes within the assigned listing cohort.

The legacy churn name is retained for imports. It never estimates Toronto market entry/exit.
"""
from datetime import date

OWNER = 'TV1 — Dương Nhật Huy'
IMPLEMENTED = True
READY = True  # Integration validated; see docs/VERIFICATION.md.

SUMMARY_FIELDS = ['snapshot_date', 'cohort_basis', 'cohort_size', 'observed_listings',
                  'missing_listings', 'coverage', 'observed_hosts', 'host_id_unusable',
                  'room_type_missing']
TRANSITION_FIELDS = ['previous_snapshot', 'snapshot_date', 'previous_n', 'current_n',
                     'new', 'retained', 'disappeared', 'entry_rate', 'exit_rate',
                     'host_comparable', 'host_changed', 'host_change_rate', 'host_pairs_excluded',
                     'room_type_comparable', 'room_type_changed', 'room_type_change_rate',
                     'room_type_pairs_excluded']


def _identifier(value):
    if not isinstance(value, str) or not value.strip().isascii() or not value.strip().isdigit():
        raise ValueError('listing_id must be an exact nonempty digit string, never float/int')
    return value.strip()


def _text(value, field):
    if value is None:
        return ''
    if not isinstance(value, str):
        raise ValueError(f'{field} must be text or None')
    text = value.strip()
    return '' if text.casefold() in {'nan', 'null', 'none'} else text


def _index(listings, snapshots):
    snapshots = list(snapshots)
    if not snapshots or any(not isinstance(s, str) or date.fromisoformat(s).isoformat() != s for s in snapshots):
        raise ValueError('snapshots must contain YYYY-MM-DD dates')
    if snapshots != sorted(set(snapshots)):
        raise ValueError('snapshots must be unique and chronological')
    indexed = {snapshot: {} for snapshot in snapshots}
    for row in listings:
        snapshot = row['snapshot_date']
        if snapshot not in indexed:
            raise ValueError(f'Unexpected snapshot: {snapshot}')
        identity = _identifier(row['listing_id'])
        if identity in indexed[snapshot]:
            raise ValueError(f'Duplicate listing in snapshot {snapshot}: {identity}; resolve QA upstream')
        indexed[snapshot][identity] = {'host_id': _text(row['host_id'], 'host_id'),
                                      'room_type': _text(row['room_type'], 'room_type')}
    return snapshots, indexed


def _valid_host(value):
    return bool(value) and value.isascii() and value.isdigit()


def _rate(numerator, denominator):
    return numerator / denominator if denominator else None


def cohort_summary(listings, snapshots, expected_ids=None):
    """One row/snapshot; denominator is the assignment, or observed union for fixtures.

    Input is an iterable of snapshot_date/listing_id/host_id/room_type. No mutation, prices,
    downloads or cleaning. Missing and malformed host IDs are explicitly unusable.
    """
    snapshots, indexed = _index(listings, snapshots)
    observed_union = set().union(*(set(group) for group in indexed.values()))
    expected = observed_union if expected_ids is None else {_identifier(key) for key in expected_ids}
    outside = observed_union - expected
    if outside:
        raise ValueError(f'Listings outside the assigned cohort: {sorted(outside)}')
    result = []
    for snapshot in snapshots:
        records = list(indexed[snapshot].values())
        hosts = [row['host_id'] for row in records if _valid_host(row['host_id'])]
        result.append({'snapshot_date': snapshot,
                       'cohort_basis': 'observed_union' if expected_ids is None else 'assignment',
                       'cohort_size': len(expected), 'observed_listings': len(records),
                       'missing_listings': len(expected - indexed[snapshot].keys()),
                       'coverage': _rate(len(records), len(expected)),
                       'observed_hosts': len(set(hosts)), 'host_id_unusable': len(records) - len(hosts),
                       'room_type_missing': sum(not row['room_type'] for row in records)})
    return result


def churn(listings, snapshots):
    """Adjacent observations and matched attribute changes, not market or ownership churn.

    new/disappeared are presence diagnostics within the supplied cohort. Legacy entry_rate
    is new/current_n, exit_rate is disappeared/previous_n; no denominator gives None.
    Host rates compare retained IDs with usable host IDs in both snapshots. Room-type rates
    compare nonempty reported values; category QA remains upstream. First appearance/absence
    and a changed host_id cannot establish market entry, exit or a legal ownership change.
    """
    snapshots, indexed = _index(listings, snapshots)
    result = []
    for previous, current in zip(snapshots, snapshots[1:]):
        before, after = indexed[previous], indexed[current]
        retained = before.keys() & after.keys()
        new, disappeared = after.keys() - before.keys(), before.keys() - after.keys()
        host_pairs = [key for key in retained if _valid_host(before[key]['host_id'])
                      and _valid_host(after[key]['host_id'])]
        room_pairs = [key for key in retained if before[key]['room_type'] and after[key]['room_type']]
        host_changed = sum(before[key]['host_id'] != after[key]['host_id'] for key in host_pairs)
        room_changed = sum(before[key]['room_type'] != after[key]['room_type'] for key in room_pairs)
        result.append({'previous_snapshot': previous, 'snapshot_date': current,
                       'previous_n': len(before), 'current_n': len(after),
                       'new': len(new), 'retained': len(retained), 'disappeared': len(disappeared),
                       'entry_rate': _rate(len(new), len(after)),
                       'exit_rate': _rate(len(disappeared), len(before)),
                       'host_comparable': len(host_pairs), 'host_changed': host_changed,
                       'host_change_rate': _rate(host_changed, len(host_pairs)),
                       'host_pairs_excluded': len(retained) - len(host_pairs),
                       'room_type_comparable': len(room_pairs), 'room_type_changed': room_changed,
                       'room_type_change_rate': _rate(room_changed, len(room_pairs)),
                       'room_type_pairs_excluded': len(retained) - len(room_pairs)})
    return result
