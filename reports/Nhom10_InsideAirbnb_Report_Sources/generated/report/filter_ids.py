    assigned_ids = assignment.review_ids if name == 'reviews.csv.gz' else assignment.listing_ids
    key = 'listing_id' if name == 'calendar.csv.gz' else 'id'
    for row in rows(folder / name):
        identity = row.get(key, '').strip()
        if identity not in assigned_ids:
            continue
