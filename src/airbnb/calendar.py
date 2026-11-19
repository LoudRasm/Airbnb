"""TV4 — Vũ Phạm Khánh Nam: Xử lý bảng calendar, dedupe theo snapshot và tính Calendar KPI."""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

OWNER = "TV4 — Vũ Phạm Khánh Nam"
READY = True


def aggregate(records, snapshot, window_days, listing_ids):
    """Tổng hợp availability rate trong cửa sổ `window_days` (ví dụ 90 ngày) từ `snapshot`.

    Contract output columns:
    snapshot_date, listing_id, available_days, observed_days, expected_days, availability_rate
    """
    snap_str = str(snapshot).strip()
    start = date.fromisoformat(snap_str)
    win = int(window_days)
    if win <= 0:
        raise ValueError("window_days must be positive")
    stop = start + timedelta(days=win)
    valid_ids = {str(lid).strip() for lid in listing_ids}

    counts: dict[str, list[int]] = {lid: [0, 0] for lid in valid_ids}
    seen: set[tuple[str, str, date]] = set()
    issues: Counter = Counter()

    for row in records:
        raw_date = str(row.get("date", "")).strip()[:10]
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            issues["invalid_calendar_date"] += 1
            continue

        if not (start <= day < stop):
            continue

        lid = str(row.get("listing_id", "")).strip()
        if lid not in valid_ids:
            issues["orphan_calendar"] += 1
            continue

        # Khóa dedupe trước aggregate: snapshot_date + listing_id + date
        key = (snap_str, lid, day)
        if key in seen:
            issues["duplicate_calendar"] += 1
            continue
        state = str(row.get("available", "")).strip().lower()
        if state not in {"t", "f"}:
            issues["invalid_available"] += 1
            continue

        seen.add(key)
        bucket = counts.setdefault(lid, [0, 0])
        bucket[0] += int(state == "t")
        bucket[1] += 1

    summary = [
        {
            "snapshot_date": snap_str,
            "listing_id": lid,
            "available_days": c[0],
            "observed_days": c[1],
            "expected_days": win,
            "availability_rate": round(c[0] / c[1], 6) if c[1] > 0 else None,
        }
        for lid, c in sorted(counts.items())
    ]
    missing_days = sum(win - c[1] for c in counts.values())
    if missing_days:
        issues["missing_calendar_days"] = missing_days
    return summary, dict(issues)


def metrics(calendar, listings, cfg):
    """Tổng hợp Calendar KPI theo (snapshot_date, analysis_area).

    Contract output columns:
    snapshot_date, analysis_area, availability_rate, observed_days, expected_days, listing_n
    """
    area_map: dict[tuple[str, str], str] = {}
    fallback_area: dict[str, str] = {}

    for row in listings:
        snap = str(row.get("snapshot_date", "")).strip()
        lid = str(row.get("listing_id", "")).strip()
        area = str(row.get("analysis_area") or "Unknown").strip() or "Unknown"
        if lid:
            if snap:
                area_map[(snap, lid)] = area
            fallback_area[lid] = area

    stats: dict[tuple[str, str], list] = {}

    for row in calendar:
        snap = str(row.get("snapshot_date", "")).strip()
        lid = str(row.get("listing_id", "")).strip()
        area = area_map.get((snap, lid)) or fallback_area.get(lid) or "Unknown"

        avail_days = int(row.get("available_days", 0) or 0)
        obs_days = int(row.get("observed_days", 0) or 0)
        exp_days = int(row.get("expected_days", 0) or 0)

        bucket = stats.setdefault((snap, area), [0, 0, 0, set()])
        bucket[0] += avail_days
        bucket[1] += obs_days
        bucket[2] += exp_days
        if lid:
            bucket[3].add(lid)

    kpi_rows = []
    for (snap, area), (avail_sum, obs_sum, exp_sum, lids) in sorted(stats.items()):
        rate = round(avail_sum / obs_sum, 6) if obs_sum > 0 else None
        kpi_rows.append(
            {
                "snapshot_date": snap,
                "analysis_area": area,
                "availability_rate": rate,
                "observed_days": obs_sum,
                "expected_days": exp_sum,
                "listing_n": len(lids),
                "coverage_rate": round(obs_sum / exp_sum, 6) if exp_sum else None,
            }
        )

    return kpi_rows


def weekday_weekend_breakdown(records, snapshot, window_days, listing_ids):
    """Hàm phân tích bổ trợ cho Notebook/Report: so sánh availability ngày thường (T2–T5)
    và cuối tuần (T6–CN), tuyệt đối không sử dụng giá từ calendar.
    """
    snap_str = str(snapshot).strip()
    start = date.fromisoformat(snap_str)
    win = int(window_days)
    if win <= 0:
        raise ValueError("window_days must be positive")
    stop = start + timedelta(days=win)
    valid_ids = {str(lid).strip() for lid in listing_ids}

    counts: dict[str, list[int]] = {}
    seen: set[tuple[str, str, date]] = set()

    for row in records:
        raw_date = str(row.get("date", "")).strip()[:10]
        try:
            day = date.fromisoformat(raw_date)
        except ValueError:
            continue

        if not (start <= day < stop):
            continue

        lid = str(row.get("listing_id", "")).strip()
        if lid not in valid_ids:
            continue

        key = (snap_str, lid, day)
        if key in seen:
            continue
        state = str(row.get("available", "")).strip().lower()
        if state not in {"t", "f"}:
            continue

        is_avail = int(state == "t")
        seen.add(key)
        bucket = counts.setdefault(lid, [0, 0, 0, 0])
        if day.weekday() in {4, 5, 6}:  # Fri, Sat, Sun
            bucket[2] += is_avail
            bucket[3] += 1
        else:  # Mon - Thu
            bucket[0] += is_avail
            bucket[1] += 1

    rows = []
    for lid, (wd_a, wd_o, we_a, we_o) in sorted(counts.items()):
        wd_rate = wd_a / wd_o if wd_o > 0 else 0.0
        we_rate = we_a / we_o if we_o > 0 else 0.0
        rows.append(
            {
                "snapshot_date": snap_str,
                "listing_id": lid,
                "weekday_availability_rate": round(wd_rate, 6),
                "weekend_availability_rate": round(we_rate, 6),
                "weekend_minus_weekday": round(we_rate - wd_rate, 6),
            }
        )
    return rows