"""Stream calendar; dedupe within each snapshot, aggregate a configurable window."""
from collections import Counter
from datetime import date, timedelta

def aggregate(records, snapshot, window_days, listing_ids):
    start = date.fromisoformat(snapshot)
    stop = start + timedelta(days=window_days)
    counts, seen, issues = {}, set(), Counter()
    for row in records:
        try:
            day = date.fromisoformat(row["date"])
        except (ValueError, KeyError):
            issues["invalid_calendar_date"] += 1
            continue
        if not start <= day < stop:
            continue
        lid = row.get("listing_id", "")
        key = (lid, day)
        if lid not in listing_ids:
            issues["orphan_calendar"] += 1
            continue
        if key in seen:
            issues["duplicate_calendar"] += 1
            continue
        seen.add(key)
        state = row.get("available", "").lower()
        if state not in {"t", "f"}:
            issues["invalid_available"] += 1
            continue
        bucket = counts.setdefault(lid, [0, 0])
        bucket[0] += state == "t"
        bucket[1] += 1
    result = [{"snapshot_date": snapshot, "listing_id": lid, "available_days": c[0],
               "observed_days": c[1], "expected_days": window_days,
               "availability_rate": c[0] / c[1]} for lid, c in sorted(counts.items())]
    return result, issues
