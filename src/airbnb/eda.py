from collections import Counter

def profile(listings):
    return [{"snapshot_date": s, "qa_flags": flags or "none", "count": n}
            for (s, flags), n in sorted(Counter((r["snapshot_date"], r["qa_flags"]) for r in listings).items())]
