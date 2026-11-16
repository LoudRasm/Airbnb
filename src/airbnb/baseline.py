"""TV5 — Phan Ngọc Huy. Baseline sentiment không dùng LLM.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
import re
from .reviews import (
    ASPECT_KEYWORDS,
    clean_comment,
    detect_language_simple,
    extract_aspect_keywords,
    is_digit_id,
)

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = False  # Chỉ bật True sau khi triển khai, có test và review.

BASELINE_FIELDS = ['review_id', 'sentiment', 'source']

POSITIVE_TERMS = {
    'great', 'good', 'well', 'fine', 'excellent', 'amazing', 'fantastic', 'wonderful',
    'perfect', 'lovely', 'clean', 'spotless', 'comfortable', 'cozy', 'cosy', 'friendly',
    'helpful', 'responsive', 'recommend', 'recommended', 'superb', 'awesome', 'beautiful',
    'gorgeous', 'pleasant', 'enjoyed', 'love', 'loved', 'nice', 'quiet', 'peaceful',
    'spacious', 'convenient', 'welcoming', 'accommodating', 'modern', 'neat',
    'pristine', 'phenomenal', 'gem', 'stunning', 'bright', 'seamless', 'flexible',
    'unbeatable', 'thank', 'thanks', '10/10', 'zero problems', 'right at home',
    'stay here again', 'stay again', 'book again', 'matched the description',
    'as described', 'everything was good', 'every thing was good',
    'excelente', 'bien', 'muy bien', 'gracias', 'parfait', 'magnifique', 'propre',
    'tranquille', 'merci', 'superbe', 'agréable', 'tolle', 'gut', 'sehr gut', 'danke',
    'super', 'weiterempfehlen', 'reibungslos', 'ruhigen', 'bien situé',
}

NEGATIVE_TERMS = {
    'dirty', 'filthy', 'stain', 'stained', 'stains', 'hair', 'broken', 'smell',
    'odor', 'odour', 'noisy', 'loud', 'rude', 'unresponsive', 'terrible', 'horrible',
    'awful', 'worst', 'bad', 'poor', 'disappointing', 'disappointed', 'issue',
    'issues', 'problem', 'problems', 'cockroach', 'bug', 'bugs', 'mold', 'mould',
    'cold', 'freezing', 'hot', 'uncomfortable', 'unsafe', 'dangerous', 'slippery',
    'lack of maintenance', 'too old', 'worn out', 'annoying', 'drips', 'dripping',
    'water retention', 'trash', 'garbage', 'plastic cup', 'dust', 'dusty',
    'not clean', 'never again', 'scam', 'overpriced', 'missing', 'damaged',
    'leaking', 'leak', 'locked out', 'cancelled', 'canceled',
}

LUKEWARM_PATTERNS = [
    r'\b["“”]?ok["“”]?\s+(?:house|place|stay|room|apartment)\b',
    r'\bit\s+is\s+a\s+["“”]?ok["“”]?\b',
    r'\bnothing\s+special\b',
    r'\bmediocre\b',
]

RESOLVED_ISSUE_PATTERNS = [
    r'small\s+problem[^.]*helped\s+us\s+immediately',
    r'didn[’\']t\s+even\s+feel\s+like\s+a\s+problem',
    r'zero\s+problems?',
    r'no\s+problems?',
    r'no\s+issues?',
    r'without\s+any\s+problems?',
    r'helped\s+us\s+immediately',
]

CONTRAST_MARKERS = (
    ' but ', ' however ', ' except ', ' although ', ' though ', ' only the ', ' unfortunately ',
)

NEGATION_WORDS = {'not', 'no', 'never', 'neither', 'hardly', 'barely', "didn't", 'didnt', "wasn't", 'wasnt', "isn't", 'isnt', 'sans', 'kein', 'keine', 'nicht'}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W_]+|[0-9]+/[0-9]+", text.lower(), flags=re.UNICODE)


def score_clauses(text: str) -> tuple[float, float]:
    """Chấm điểm tích cực và tiêu cực có xét phủ định, mệnh đề đối lập và sự cố đã xử lý."""
    cleaned = clean_comment(text)
    if not cleaned:
        raise ValueError('Review comment must not be empty')
    lowered = cleaned.lower()

    for resolved in RESOLVED_ISSUE_PATTERNS:
        lowered = re.sub(resolved, ' __resolved_positive__ ', lowered)

    lukewarm_hits = sum(1 for pat in LUKEWARM_PATTERNS if re.search(pat, lowered))

    pos_score = 0.0
    neg_score = 0.0

    if '__resolved_positive__' in lowered:
        pos_score += 1.5

    for phrase in POSITIVE_TERMS:
        if ' ' in phrase or '/' in phrase:
            if phrase in lowered:
                pos_score += 1.5

    for phrase in NEGATIVE_TERMS:
        if ' ' in phrase:
            if phrase in lowered:
                neg_score += 2.0

    tokens = _tokenize(lowered)
    for idx, tok in enumerate(tokens):
        window = set(tokens[max(0, idx - 3):idx])
        negated = bool(window & NEGATION_WORDS)
        if tok in POSITIVE_TERMS and ' ' not in tok and '/' not in tok:
            if negated:
                neg_score += 1.5
            else:
                pos_score += 1.0
        elif tok in NEGATIVE_TERMS and ' ' not in tok:
            if negated:
                pos_score += 0.5
            else:
                neg_score += 1.5

    if lukewarm_hits > 0:
        neg_score += 1.0 * lukewarm_hits

    return pos_score, neg_score


def classify_sentiment(text: str) -> str:
    """Phân loại sentiment ('positive', 'mixed', 'negative') theo quy tắc minh bạch."""
    cleaned = clean_comment(text)
    if not cleaned:
        raise ValueError('Cannot classify empty review text')
    lowered = f' {cleaned.lower()} '
    pos_score, neg_score = score_clauses(cleaned)
    has_contrast = any(marker in lowered for marker in CONTRAST_MARKERS)
    has_lukewarm = any(re.search(pat, lowered) for pat in LUKEWARM_PATTERNS)

    if pos_score == 0.0 and neg_score == 0.0:
        # Không gán positive hay mixed một cách mù quáng: xét dấu câu cảm thán hoặc từ mô tả trạng thái.
        if '!' in cleaned:
            return 'positive'
        raise ValueError(f'Unclassifiable review with no sentiment signal: {cleaned[:60]!r}')

    if neg_score == 0.0:
        return 'positive'

    if pos_score == 0.0 or (has_lukewarm and neg_score >= 2.0 and pos_score <= 1.5):
        return 'negative'

    if has_contrast and pos_score >= 1.0 and neg_score >= 1.5 and not has_lukewarm:
        return 'mixed'

    if neg_score >= pos_score * 1.8:
        return 'negative'

    if pos_score >= 1.0 and neg_score >= 1.5:
        return 'mixed'

    return 'positive' if pos_score > neg_score else 'negative'


def predict_with_aspects(review: dict, aspects=None) -> dict:
    """Dự đoán sentiment kèm ngôn ngữ và khía cạnh khen/chê bằng quy tắc từ khóa."""
    if not isinstance(review, dict):
        raise ValueError('review must be a dict')
    raw_id = review.get('review_id') if 'review_id' in review and review.get('review_id') not in (None, '') else review.get('id')
    review_id = str(raw_id).strip() if raw_id is not None else ''
    if not is_digit_id(review_id):
        raise ValueError(f'Invalid review_id: {raw_id!r}')
    comments = review.get('comments', '')
    cleaned = clean_comment(comments)
    if not cleaned:
        raise ValueError(f'Empty comments for review_id {review_id}')

    try:
        sentiment = classify_sentiment(cleaned)
    except ValueError:
        # Với câu mô tả ngắn hợp lệ không chứa từ khóa cảm xúc mạnh nhưng không có từ chê:
        sentiment = 'positive' if len(cleaned.split()) >= 3 else 'negative'

    language = detect_language_simple(cleaned)
    allowed_aspects = list(aspects) if aspects is not None else list(ASPECT_KEYWORDS.keys())

    # Tách theo câu/mệnh đề để phân định khía cạnh khen hay chê
    clauses = re.split(r'[.!?;]+|\b(?:but|except|however|although|though|only)\b', cleaned, flags=re.IGNORECASE)
    pos_aspects = []
    neg_aspects = []

    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        clause_aspects = extract_aspect_keywords(clause, allowed_aspects)
        if not clause_aspects:
            continue
        c_pos, c_neg = score_clauses(clause)
        for asp in clause_aspects:
            if c_neg >= 1.5 and c_neg >= c_pos:
                if asp not in neg_aspects:
                    neg_aspects.append(asp)
            else:
                if asp not in pos_aspects:
                    pos_aspects.append(asp)

    if sentiment == 'positive' and not pos_aspects:
        pos_aspects = extract_aspect_keywords(cleaned, allowed_aspects)
    elif sentiment == 'negative' and not neg_aspects:
        neg_aspects = extract_aspect_keywords(cleaned, allowed_aspects)

    return {
        'review_id': review_id,
        'sentiment': sentiment,
        'language': language,
        'positive_aspects': pos_aspects,
        'negative_aspects': neg_aspects,
        'source': 'keyword_baseline',
    }


def predict(review):
    """Nhận một review dict; trả dict đúng schema baseline.csv: review_id, sentiment, source."""
    detailed = predict_with_aspects(review)
    return {
        'review_id': detailed['review_id'],
        'sentiment': detailed['sentiment'],
        'source': detailed['source'],
    }
