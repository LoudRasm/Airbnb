    counts: dict[str, list[int]] = {lid: [0, 0] for lid in valid_ids}
    seen: set[tuple[str, str, date]] = set()
    issues: Counter = Counter()

