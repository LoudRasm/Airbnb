"""TV3 listings and host KPIs. Prices exclude invalid/outlier flags."""
from collections import Counter, defaultdict
from statistics import median

def summarize(listings, calendar, currency):
    groups = defaultdict(list)
    for row in listings:
        groups[(row["snapshot_date"], "ALL")].append(row)
        groups[(row["snapshot_date"], row["neighbourhood_cleansed"] or "UNKNOWN")].append(row)
    cal = {(r["snapshot_date"], r["listing_id"]): r for r in calendar}
    host_counts = Counter((r["snapshot_date"], r["host_id"]) for r in listings if r["host_id"])
    result = []
    for (snapshot, area), group in sorted(groups.items()):
        prices = [r["price"] for r in group if r["price"] is not None and "price_outlier" not in r["qa_flags"]]
        hosts = [r for r in group if r["host_id"]]
        days = [cal[(snapshot, r["listing_id"])] for r in group if (snapshot, r["listing_id"]) in cal]
        observed = sum(d["observed_days"] for d in days)
        result.append({"snapshot_date": snapshot, "neighbourhood": area, "supply": len(group),
                       "median_price": median(prices) if prices else "", "price_n": len(prices), "currency": currency,
                       "entire_home_share": sum(r["room_type"] == "Entire home/apt" for r in group)/len(group),
                       "multi_listing_host_share": sum(host_counts[(snapshot, r["host_id"])] > 1 for r in hosts)/len(hosts) if hosts else "",
                       "availability_rate": sum(d["available_days"] for d in days)/observed if observed else "",
                       "calendar_coverage": observed/sum(d["expected_days"] for d in days) if days else ""})
    return result

def guest_kpi(predictions):
    if not predictions:
        return []
    return [{"metric": "sample_guest_issue_rate", "value": sum(r["sentiment"] in {"mixed", "negative"} for r in predictions)/len(predictions),
             "sample_n": len(predictions), "source": "LLM", "scope": "deduplicated review sample; not population estimate"}]
