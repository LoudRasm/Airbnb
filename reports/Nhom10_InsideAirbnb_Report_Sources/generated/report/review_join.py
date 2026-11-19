        # Join source listing_id; never ask the model to invent IDs or filter reviews by listing cohort.
        linked = [{**p, 'listing_id': review_map[p['review_id']]['listing_id']} for p in predictions]
        tables['guest_kpi'] = review_kpi.guest_kpi(linked, listings, cfg)
