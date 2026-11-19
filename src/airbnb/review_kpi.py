"""TV5 — Phan Ngọc Huy. KPI trải nghiệm khách hàng từ kết quả phân tích review.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
from collections import Counter, defaultdict
import json

from .llm import SENTIMENTS
from .reviews import is_digit_id

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = True  # Integration validated; see docs/VERIFICATION.md.

GUEST_KPI_FIELDS = ['metric', 'value', 'sample_n', 'source', 'scope']


def _parse_aspect_list(value) -> list[str]:
    if value is None or value == '':
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        text = value.strip()
        if text.startswith('['):
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        return [item.strip() for item in text.split(',') if item.strip()]
    raise ValueError(f'Unsupported aspect list value: {value!r}')


def _dedupe_listing_areas(listings) -> dict[str, str]:
    """Ánh xạ mỗi listing_id duy nhất sang analysis_area (không nhân bản theo nhiều mốc)."""
    if not listings:
        return {}
    by_listing = {}
    for row in listings:
        if not isinstance(row, dict):
            continue
        raw_lid = row.get('listing_id') if 'listing_id' in row and row.get('listing_id') not in (None, '') else row.get('id')
        lid = str(raw_lid).strip() if raw_lid is not None else ''
        if not lid:
            continue
        snap = str(row.get('snapshot_date', ''))
        area = str(row.get('analysis_area') or row.get('neighbourhood_cleansed') or '').strip()
        if not area:
            continue
        prev = by_listing.get(lid)
        if prev is None or snap >= prev[0]:
            by_listing[lid] = (snap, area)
    return {lid: pair[1] for lid, pair in by_listing.items()}


def guest_kpi(predictions, listings, cfg):
    """Trả list[dict] đúng schema kpi_guest.csv:
    metric, value, sample_n, source, scope.

    Mỗi review_id chỉ được tính đúng 1 lần (không nhân bản theo snapshot).
    """
    preds = list(predictions or [])
    if not preds:
        return []

    seen_ids = set()
    sentiment_counts = Counter()
    pos_aspect_counts = Counter()
    neg_aspect_counts = Counter()
    sources = set()

    for row in preds:
        if not isinstance(row, dict):
            raise ValueError('Each prediction must be a dict')
        raw_id = row.get('review_id') if 'review_id' in row and row.get('review_id') not in (None, '') else row.get('id')
        rid = str(raw_id).strip() if raw_id is not None else ''
        if not is_digit_id(rid):
            raise ValueError(f'Invalid review_id in predictions: {raw_id!r}')
        if rid in seen_ids:
            raise ValueError(f'Duplicate review_id in predictions: {rid} (must be deduplicated across snapshots)')
        seen_ids.add(rid)

        sentiment = row.get('sentiment')
        if not isinstance(sentiment, str) or sentiment not in SENTIMENTS:
            raise ValueError(f'Invalid sentiment for review_id {rid}: {sentiment!r}')
        sentiment_counts[sentiment] += 1

        if row.get('source'):
            sources.add(str(row['source']))

        for asp in set(_parse_aspect_list(row.get('positive_aspects'))):
            pos_aspect_counts[asp] += 1
        for asp in set(_parse_aspect_list(row.get('negative_aspects'))):
            neg_aspect_counts[asp] += 1

    sample_n = len(preds)
    source_name = sorted(sources)[0] if len(sources) == 1 else (cfg.get('llm', {}).get('model', 'llm') if not sources else '+'.join(sorted(sources)))
    base_scope = 'assigned_review_baseline' if 'keyword_baseline' in source_name else 'assigned_llm_sample'

    issue_count = sentiment_counts['mixed'] + sentiment_counts['negative']
    rows = [
        {
            'metric': 'guest_issue_rate',
            'value': round(issue_count / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        },
        {
            'metric': 'positive_sentiment_rate',
            'value': round(sentiment_counts['positive'] / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        },
        {
            'metric': 'mixed_sentiment_rate',
            'value': round(sentiment_counts['mixed'] / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        },
        {
            'metric': 'negative_sentiment_rate',
            'value': round(sentiment_counts['negative'] / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        },
    ]

    aspects = list(cfg.get('llm', {}).get('aspects') or [])
    for aspect in aspects:
        rows.append({
            'metric': f'negative_aspect_{aspect}_rate',
            'value': round(neg_aspect_counts[aspect] / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        })
        rows.append({
            'metric': f'positive_aspect_{aspect}_rate',
            'value': round(pos_aspect_counts[aspect] / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': base_scope,
        })

    # Ghép thêm thông tin listing (nếu có listing_id trên review) không nhân số review theo nhiều mốc
    listing_areas = _dedupe_listing_areas(listings)
    has_listing_id = any(row.get('listing_id') for row in preds)
    if listing_areas and has_listing_id:
        matched_n = 0
        area_totals = Counter()
        area_issues = Counter()
        for row in preds:
            lid = str(row.get('listing_id') or '').strip()
            area = listing_areas.get(lid)
            if area:
                matched_n += 1
                area_totals[area] += 1
                if row['sentiment'] in {'mixed', 'negative'}:
                    area_issues[area] += 1
        rows.append({
            'metric': 'listing_cohort_join_coverage',
            'value': round(matched_n / sample_n, 6),
            'sample_n': sample_n,
            'source': source_name,
            'scope': 'assigned_listing_cohort_join',
        })
        for area in sorted(area_totals):
            total_a = area_totals[area]
            rows.append({
                'metric': 'area_guest_issue_rate',
                'value': round(area_issues[area] / total_a, 6),
                'sample_n': total_a,
                'source': source_name,
                'scope': f'analysis_area:{area}',
            })

    return rows
