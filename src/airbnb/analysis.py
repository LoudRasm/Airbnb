"""TV1 market dynamics. Entry/exit refer to observed snapshots, not business closures."""
def churn(listings, snapshots):
    sets = {s: {r["listing_id"] for r in listings if r["snapshot_date"] == s} for s in snapshots}
    result = []
    for prev, curr in zip(snapshots, snapshots[1:]):
        a, b = sets[prev], sets[curr]
        result.append({"previous_snapshot": prev, "snapshot_date": curr,
                       "new": len(b-a), "retained": len(a&b), "disappeared": len(a-b),
                       "entry_rate": len(b-a)/len(b) if b else "",
                       "exit_rate": len(a-b)/len(a) if a else ""})
    return result
