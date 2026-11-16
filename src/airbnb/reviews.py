"""TV5 — Phan Ngọc Huy. Thu thập, kiểm tra chất lượng và tiền xử lý reviews.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
from collections import Counter
from datetime import date
import hashlib
import html
import json
import re

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = False  # Chỉ bật True sau khi triển khai, có test và review.

REVIEW_FIELDS = ['review_id', 'listing_id', 'date', 'comments', 'first_seen_snapshot']
TEXT_HASH_FIELDS = ('review_id', 'listing_id', 'date', 'comments')

HTML_TAG_RE = re.compile(r'<[^>]+>')
WHITESPACE_RE = re.compile(r'\s+')

ASPECT_KEYWORDS = {
    'location': [
        'location', 'neighbourhood', 'neighborhood', 'downtown', 'subway', 'metro',
        'transit', 'station', 'walk', 'walking', 'streetcar', 'bus', 'central',
        'close to', 'proximity', 'situé', 'ubicacion', 'ubicación', 'lage',
    ],
    'cleanliness': [
        'clean', 'spotless', 'tidy', 'neat', 'dirty', 'stain', 'stained', 'hair',
        'dust', 'filthy', 'smell', 'odor', 'odour', 'mold', 'mould', 'bug',
        'cockroach', 'trash', 'garbage', 'hygiene', 'propre', 'limpio', 'sauber',
    ],
    'host': [
        'host', 'hosts', 'responsive', 'communicative', 'communication', 'helpful',
        'friendly', 'welcoming', 'accommodating', 'hospitality', 'kind', 'rude',
        'unresponsive', 'polite', 'superhost', 'hôte', 'anfitrión', 'gastgeber',
    ],
    'value': [
        'value', 'price', 'priced', 'worth', 'affordable', 'expensive', 'overpriced',
        'cheap', 'money', 'cost', 'budget', 'deal', 'qualité-prix', 'precio',
    ],
    'amenities': [
        'kitchen', 'bed', 'beds', 'mattress', 'pillow', 'sheet', 'sheets', 'towel',
        'wifi', 'wi-fi', 'internet', 'tv', 'shower', 'bathroom', 'sink', 'ac',
        'air conditioning', 'heating', 'heater', 'parking', 'washer', 'dryer',
        'coffee', 'balcony', 'terrace', 'equipped', 'stocked', 'furniture', 'sofa',
    ],
    'noise': [
        'noise', 'noisy', 'quiet', 'peaceful', 'loud', 'soundproofing', 'soundproof',
        'traffic', 'construction', 'party', 'thin walls', 'bruit', 'calme', 'tranquille',
        'ruido', 'ruhig',
    ],
    'safety': [
        'safe', 'safety', 'secure', 'secured', 'security', 'unsafe', 'sketchy',
        'dangerous', 'lock', 'slippery', 'hazard', 'alarm', 'sécurité', 'seguro',
    ],
    'check-in': [
        'check in', 'check-in', 'checkin', 'check out', 'check-out', 'checkout',
        'key', 'keys', 'keypad', 'lockbox', 'door code', 'instructions', 'arrival',
        'early check', 'late check',
    ],
}

LANG_STOPWORDS = {
    'en': {'the', 'and', 'was', 'very', 'stay', 'place', 'with', 'for', 'great', 'clean', 'host', 'we', 'had'},
    'fr': {'très', 'tres', 'bien', 'dans', 'avec', 'pour', 'nous', 'avons', 'séjour', 'endroit', 'est', 'une', 'des', 'les'},
    'es': {'muy', 'todo', 'excelente', 'con', 'para', 'una', 'del', 'las', 'los', 'casa', 'limpio', 'estancia', 'lugar'},
    'de': {'und', 'die', 'der', 'das', 'in', 'einer', 'mit', 'war', 'sehr', 'wir', 'hatten', 'wohnung', 'für', 'ist'},
    'pt': {'muito', 'com', 'para', 'uma', 'foi', 'lugar', 'limpo', 'ótima', 'excelente', 'casa', 'estadia'},
}


def is_digit_id(value) -> bool:
    """Kiểm tra ID là chuỗi chữ số ASCII không rỗng (không ép kiểu int/float)."""
    return isinstance(value, str) and bool(value) and value.isascii() and value.isdigit()


def valid_iso_date(value) -> bool:
    """Kiểm tra chuỗi ngày định dạng YYYY-MM-DD."""
    if not isinstance(value, str) or len(value) != 10:
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def clean_comment(text: str) -> str:
    """Làm sạch HTML tag (<br/>) và khoảng trắng thừa trong nội dung review."""
    if not isinstance(text, str):
        return ''
    unescaped = html.unescape(text)
    without_tags = HTML_TAG_RE.sub(' ', unescaped)
    return WHITESPACE_RE.sub(' ', without_tags).strip()


def record_text_sha256(row: dict) -> str:
    """Tính SHA-256 cho các trường văn bản gốc của review khớp manifest."""
    payload = json.dumps(
        {key: str(row.get(key, '')) for key in TEXT_HASH_FIELDS},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def comment_sha256(text: str) -> str:
    """Tính SHA-256 trên nội dung comments chuẩn hóa."""
    return hashlib.sha256((text or '').encode('utf-8')).hexdigest()


def detect_language_simple(text: str) -> str:
    """Nhận diện ngôn ngữ dựa trên bộ ký tự Unicode và từ khóa đặc trưng."""
    cleaned = clean_comment(text)
    if not cleaned:
        return 'unknown'
    for ch in cleaned:
        code = ord(ch)
        if 0x4E00 <= code <= 0x9FFF:
            return 'zh'
        if 0xAC00 <= code <= 0xD7AF:
            return 'ko'
        if 0x3040 <= code <= 0x30FF:
            return 'ja'
    tokens = re.findall(r"[^\W\d_]+", cleaned.lower(), flags=re.UNICODE)
    if not tokens:
        return 'unknown'
    token_set = set(tokens)
    scores = {lang: len(token_set & words) for lang, words in LANG_STOPWORDS.items()}
    best_lang, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        if best_score == scores['en'] and scores['en'] > 0:
            return 'en'
        return best_lang
    return 'en' if cleaned.isascii() else 'unknown'


def extract_aspect_keywords(text: str, aspects=None) -> list[str]:
    """Trích xuất danh sách khía cạnh xuất hiện trong câu dựa trên từ khóa."""
    cleaned = clean_comment(text).lower()
    if not cleaned:
        return []
    allowed = list(aspects) if aspects is not None else list(ASPECT_KEYWORDS.keys())
    matched = []
    for aspect in allowed:
        keywords = ASPECT_KEYWORDS.get(aspect, [])
        for kw in keywords:
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, cleaned):
                matched.append(aspect)
                break
    return matched


def collect(records, snapshot, existing):
    """Cập nhật dict existing review_id -> review record; trả issue_counts.

    Giữ review_id/listing_id dạng chuỗi chữ số chính xác.
    Kiểm tra trùng trong cùng mốc, trùng giữa các mốc và xung đột nội dung
    (review_text_collision) để đảm bảo văn bản khớp phiên bản mốc mới nhất.
    """
    if not valid_iso_date(snapshot):
        raise ValueError(f'Invalid snapshot date: {snapshot!r}')
    if not isinstance(existing, dict):
        raise ValueError('existing must be a dict mapping review_id -> record')

    issues = Counter()
    seen_in_snapshot = {}

    for row in records:
        if not isinstance(row, dict):
            issues['invalid_review_record'] += 1
            continue

        raw_id = row.get('review_id') if 'review_id' in row and row.get('review_id') not in (None, '') else row.get('id')
        review_id = raw_id.strip() if isinstance(raw_id, str) else ''
        if not is_digit_id(review_id):
            issues['invalid_review_id'] += 1
            continue

        raw_listing = row.get('listing_id')
        listing_id = raw_listing.strip() if isinstance(raw_listing, str) else ''
        if not is_digit_id(listing_id):
            issues['invalid_listing_id'] += 1
            continue

        raw_date = row.get('date')
        review_date = raw_date.strip() if isinstance(raw_date, str) else ''
        if not valid_iso_date(review_date):
            issues['invalid_review_date'] += 1
            continue

        raw_comments = row.get('comments')
        if not isinstance(raw_comments, str) or not clean_comment(raw_comments):
            issues['empty_review_comment'] += 1
            continue

        candidate = {
            'review_id': review_id,
            'listing_id': listing_id,
            'date': review_date,
            'comments': raw_comments,
        }

        if review_id in seen_in_snapshot:
            issues['duplicate_review_in_snapshot'] += 1
            prev_in_snap = seen_in_snapshot[review_id]
            if (prev_in_snap['comments'] != raw_comments
                    or prev_in_snap['listing_id'] != listing_id
                    or prev_in_snap['date'] != review_date):
                issues['review_text_collision'] += 1
            continue

        seen_in_snapshot[review_id] = candidate

        if review_id in existing:
            issues['duplicate_review_across_snapshots'] += 1
            prev = existing[review_id]
            if (prev.get('comments') != raw_comments
                    or prev.get('listing_id') != listing_id
                    or prev.get('date') != review_date):
                issues['review_text_collision'] += 1
                existing[review_id] = {
                    **candidate,
                    'first_seen_snapshot': prev.get('first_seen_snapshot', snapshot),
                }
        else:
            existing[review_id] = {
                **candidate,
                'first_seen_snapshot': snapshot,
            }

    return dict(issues)
