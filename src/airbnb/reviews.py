from datetime import date

def collect(records, snapshot, existing):
    issues = {"duplicate_review_across_or_within_snapshots": 0, "invalid_review": 0, "review_collision": 0}
    for row in records:
        rid, lid = row.get("id", ""), row.get("listing_id", "")
        try:
            day = date.fromisoformat(row.get("date", ""))
            valid = day <= date.fromisoformat(snapshot)
        except ValueError:
            valid = False
        if not rid or not lid or not row.get("comments", "").strip() or not valid:
            issues["invalid_review"] += 1
            continue
        new = {"review_id": rid, "listing_id": lid, "date": row["date"],
               "comments": row["comments"], "first_seen_snapshot": snapshot}
        if rid in existing:
            issues["duplicate_review_across_or_within_snapshots"] += 1
            if any(existing[rid][k] != new[k] for k in ["listing_id", "date", "comments"]):
                issues["review_collision"] += 1
            continue
        existing[rid] = new
    return issues
