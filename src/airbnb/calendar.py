"""TV4 — Vũ Phạm Khánh Nam. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV4 — Vũ Phạm Khánh Nam'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


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
def calculate_weekend_pricing_premium(records, snapshot, window_days, listing_ids):
    """Phân tích chênh lệch giá niêm yết giữa ngày thường (T2-T5) và cuối tuần (T6-CN)."""
    start = date.fromisoformat(snapshot)
    stop = start + timedelta(days=window_days)
    price_store = {}
    
    for row in records:
        try:
            day = date.fromisoformat(row["date"])
        except (ValueError, KeyError):
            continue
            
        if not (start <= day < stop):
            continue
            
        lid = row.get("listing_id", "")
        if lid not in listing_ids:
            continue
            
        raw_price = str(row.get("price", "")).replace("$", "").replace(",", "").strip()
        try:
            price_val = float(raw_price)
        except ValueError:
            continue
            
        if lid not in price_store:
            price_store[lid] = {"weekday": [], "weekend": []}
        if day.weekday() in {4, 5, 6}:
            price_store[lid]["weekend"].append(price_val)
        else:
            price_store[lid]["weekday"].append(price_val)
            
    summary = []
    for lid, pdata in sorted(price_store.items()):
        weekday_prices = pdata["weekday"]
        weekend_prices = pdata["weekend"]
        
        avg_weekday = sum(weekday_prices) / len(weekday_prices) if weekday_prices else 0.0
        avg_weekend = sum(weekend_prices) / len(weekend_prices) if weekend_prices else 0.0
        
        premium_pct = 0.0
        if avg_weekday > 0:
            premium_pct = ((avg_weekend - avg_weekday) / avg_weekday) * 100
            
        summary.append({
            "snapshot_date": snapshot,
            "listing_id": lid,
            "avg_price_weekday": round(avg_weekday, 2),
            "avg_price_weekend": round(avg_weekend, 2),
            "weekend_premium_pct": round(premium_pct, 2)
        })
        
    return summary
