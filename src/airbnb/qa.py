"""Starter rules: flags preserve anomalies; invalid keys and duplicates are excluded."""
from collections import Counter
from statistics import median

def number(value):
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None

def clean_listings(records, snapshot, cfg):
    cleaned, seen, counts = [], set(), Counter()
    prices_before = []
    for row in records:
        price = number(row.get("price"))
        if price is not None and price == price and abs(price) != float("inf"):
            prices_before.append(price)
        key = row.get("id", "").strip()
        if not key:
            counts["missing_id"] += 1
            continue
        if key in seen:
            counts["duplicate_listing"] += 1
            continue
        seen.add(key)
        flags = []
        if price is None or price != price or abs(price) == float("inf"):
            price = None
            flags.append("invalid_price")
        elif price <= 0 or price > cfg["qa"]["price_max"]:
            flags.append("price_outlier")
        if row.get("room_type") not in cfg["qa"]["room_types"]:
            flags.append("category_drift")
        if not row.get("neighbourhood_cleansed"):
            flags.append("missing_area")
        if not row.get("host_id"):
            flags.append("missing_host")
        nights = number(row.get("minimum_nights"))
        if nights is None or nights < 1 or nights > cfg["qa"]["min_nights_cap"]:
            flags.append("invalid_minimum_nights")
        counts.update(flags)
        cleaned.append({"snapshot_date": snapshot, "listing_id": key,
                        "host_id": row.get("host_id", ""), "price": price,
                        "room_type": row.get("room_type", ""),
                        "neighbourhood_cleansed": row.get("neighbourhood_cleansed", ""),
                        "latitude": number(row.get("latitude")), "longitude": number(row.get("longitude")),
                        "qa_flags": "|".join(flags)})
    valid = [r["price"] for r in cleaned if r["price"] is not None and "price_outlier" not in r["qa_flags"]]
    report = [{"snapshot_date": snapshot, "rule": rule, "affected_rows": counts[rule],
               "action": "exclude" if rule in {"missing_id", "duplicate_listing"} else "flag",
               "rows_after": len(cleaned),
               "median_price_before": median(prices_before) if prices_before else "",
               "median_price_after": median(valid) if valid else ""}
              for rule in ["missing_id", "duplicate_listing", "invalid_price", "price_outlier", "category_drift", "missing_area", "missing_host", "invalid_minimum_nights"]]
    return cleaned, report
