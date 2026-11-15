"""TV5 — Phan Ngọc Huy. Phân tích review bằng Gemini API có cache, retry và kiểm tra schema.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
import hashlib
import json
import os
from pathlib import Path
import random
import re
import time
import urllib.error
import urllib.request

from .reviews import clean_comment, comment_sha256, is_digit_id

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = False  # Chỉ bật True sau khi triển khai, có test và review.

SENTIMENTS = {'positive', 'mixed', 'negative'}
LLM_FIELDS = ['review_id', 'sentiment', 'language', 'positive_aspects', 'negative_aspects', 'source']
PROMPT_VERSION = 'tv5-gemini-v1'

PROMPT_TEMPLATE = """You are an expert hospitality review analyst for Airbnb listings in Toronto.
Analyze the following guest review and return ONLY a single valid JSON object (no markdown, no explanation) with this exact schema:
{{
  "sentiment": "positive" | "mixed" | "negative",
  "language": "<2-letter ISO 639-1 language code such as en, fr, es, de, zh, pt>",
  "positive_aspects": [<subset of allowed aspects praised by the guest>],
  "negative_aspects": [<subset of allowed aspects criticized by the guest>]
}}

Rules:
1. "sentiment" MUST be one of: "positive", "mixed", "negative".
   - "positive": Overall satisfied guest experience; no significant complaints (or a minor issue was immediately resolved and did not hurt the stay).
   - "mixed": Contains both genuine praise and notable complaints/drawbacks.
   - "negative": Overall dissatisfied experience or dominated by complaints/safety/cleanliness issues.
   - Do NOT use "mixed" as a fallback if uncertain; judge the actual sentiment expressed in the text.
2. Allowed aspects taxonomy: {aspects_json}
   - Every item in "positive_aspects" and "negative_aspects" MUST come strictly from this list.
   - Do not invent new aspect names. Use an empty list [] if none apply.

Guest review:
{review_text}
"""

CODE_FENCE_RE = re.compile(r'^```(?:json)?\s*|\s*```$', flags=re.IGNORECASE | re.MULTILINE)


def build_prompt(comments: str, aspects: list[str]) -> str:
    """Tạo prompt chuẩn hóa với danh mục khía cạnh từ cấu hình."""
    cleaned = clean_comment(comments)
    return PROMPT_TEMPLATE.format(
        aspects_json=json.dumps(list(aspects), ensure_ascii=False),
        review_text=cleaned,
    )


def prompt_signature(aspects: list[str]) -> str:
    """Tính SHA-256 đại diện cho phiên bản prompt và danh mục taxonomy."""
    payload = json.dumps(
        {
            'prompt_version': PROMPT_VERSION,
            'template': PROMPT_TEMPLATE,
            'aspects': list(aspects),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def strip_code_fences(raw_text: str) -> str:
    """Loại bỏ markdown code fence nếu LLM bọc JSON trong ```json ... ```."""
    if not isinstance(raw_text, str):
        raise ValueError('LLM response text must be a string')
    text = raw_text.strip()
    if text.startswith('```'):
        text = CODE_FENCE_RE.sub('', text).strip()
    return text


def validate(obj, aspects):
    """Kiểm tra JSON trả về từ LLM hoặc cache; ném ValueError nếu sai schema/taxonomy."""
    if not isinstance(obj, dict):
        raise ValueError('LLM output must be a JSON object (dict)')
    if not isinstance(aspects, (list, tuple, set)) or not aspects:
        raise ValueError('aspects taxonomy must be a non-empty collection')
    allowed_aspects = set(aspects)

    sentiment = obj.get('sentiment')
    if not isinstance(sentiment, str) or sentiment not in SENTIMENTS:
        raise ValueError(f'Invalid sentiment: {sentiment!r}; must be one of {sorted(SENTIMENTS)}')

    language = obj.get('language')
    if not isinstance(language, str) or not language.strip():
        raise ValueError(f'Invalid language: {language!r}; must be a non-empty string')
    language = language.strip().lower()

    pos_aspects = obj.get('positive_aspects')
    neg_aspects = obj.get('negative_aspects')
    if not isinstance(pos_aspects, list) or not isinstance(neg_aspects, list):
        raise ValueError('positive_aspects and negative_aspects must be JSON lists')

    clean_pos = []
    for item in pos_aspects:
        if not isinstance(item, str) or item not in allowed_aspects:
            raise ValueError(f'Invalid positive aspect {item!r}; allowed: {sorted(allowed_aspects)}')
        if item not in clean_pos:
            clean_pos.append(item)

    clean_neg = []
    for item in neg_aspects:
        if not isinstance(item, str) or item not in allowed_aspects:
            raise ValueError(f'Invalid negative aspect {item!r}; allowed: {sorted(allowed_aspects)}')
        if item not in clean_neg:
            clean_neg.append(item)

    return {
        'sentiment': sentiment,
        'language': language,
        'positive_aspects': clean_pos,
        'negative_aspects': clean_neg,
    }


def _cache_key(review_id: str, text_hash: str, model: str, p_hash: str) -> tuple[str, str, str, str]:
    return (review_id, text_hash, model, p_hash)


def load_cache(cache_path: Path, aspects: list[str], model: str, p_hash: str) -> dict[tuple, dict]:
    """Đọc cache JSONL và chỉ nhận các bản ghi khớp model, prompt/taxonomy, text_sha256 và hợp lệ."""
    cache = {}
    if not cache_path.exists():
        return cache
    with cache_path.open('r', encoding='utf-8') as stream:
        for line_no, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Corrupted JSONL cache at {cache_path}:{line_no}: {exc}') from exc
            if not isinstance(entry, dict):
                continue
            rid = entry.get('review_id')
            t_hash = entry.get('text_sha256')
            e_model = entry.get('model')
            e_phash = entry.get('prompt_sha256')
            if not (isinstance(rid, str) and isinstance(t_hash, str) and e_model == model and e_phash == p_hash):
                continue
            validated = validate(entry, aspects)
            cache[_cache_key(rid, t_hash, model, p_hash)] = {
                'review_id': rid,
                **validated,
                'source': str(entry.get('source') or model),
            }
    return cache


def append_cache(cache_path: Path, record: dict) -> None:
    """Ghi nối một bản ghi kết quả LLM kèm provenance vào file JSONL cache."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')


def call_gemini_api(prompt: str, model: str, api_key: str, timeout: float = 30.0) -> str:
    """Gọi Gemini generateContent REST API trả về chuỗi văn bản JSON."""
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'
    payload = {
        'contents': [{'parts': [{'text': prompt}]}],
        'generationConfig': {
            'temperature': 0.0,
            'responseMimeType': 'application/json',
        },
    }
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode('utf-8'))
    try:
        return body['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f'Unexpected Gemini response structure: {body!r}') from exc


def select_reviews(reviews: list[dict], cfg: dict, review_ids=None) -> list[dict]:
    """Chọn đúng tập review_ids từ workbook hoặc lấy mẫu cố định theo seed."""
    by_id = {}
    for row in reviews:
        raw_id = row.get('review_id') if 'review_id' in row and row.get('review_id') not in (None, '') else row.get('id')
        rid = str(raw_id).strip() if raw_id is not None else ''
        if not is_digit_id(rid):
            raise ValueError(f'Invalid review_id in reviews table: {raw_id!r}')
        if rid in by_id:
            raise ValueError(f'Duplicate review_id in reviews input: {rid}')
        by_id[rid] = {**row, 'review_id': rid}

    if review_ids is not None:
        target_ids = {str(rid).strip() for rid in review_ids}
        if not target_ids:
            return []
        missing = target_ids - by_id.keys()
        if missing:
            raise ValueError(f'Assigned LLM review IDs missing from reviews table: {sorted(missing)[:5]}')
        ordered_ids = sorted(target_ids, key=int)
        return [by_id[rid] for rid in ordered_ids]

    ordered = [by_id[rid] for rid in sorted(by_id, key=int)]
    sample_size = int(cfg.get('llm', {}).get('sample_size', len(ordered)))
    if len(ordered) <= sample_size:
        return ordered
    rng = random.Random(cfg.get('seed', 42))
    sampled = rng.sample(ordered, sample_size)
    return sorted(sampled, key=lambda r: int(r['review_id']))


def analyze(reviews, cfg, root, review_ids=None):
    """Phân tích tập review bằng Gemini API với cache provenance, retry và kiểm tra schema.

    Không bao giờ biến lỗi API hoặc JSON sai thành nhãn mặc định.
    """
    llm_cfg = cfg.get('llm', {})
    model = llm_cfg.get('model')
    if not isinstance(model, str) or not model.strip():
        raise ValueError('cfg["llm"]["model"] must be a non-empty string')
    aspects = list(llm_cfg.get('aspects') or [])
    if not aspects:
        raise ValueError('cfg["llm"]["aspects"] must be a non-empty list')
    retries = int(llm_cfg.get('retries', 3))
    if retries < 1:
        raise ValueError('cfg["llm"]["retries"] must be >= 1')

    cache_rel = llm_cfg.get('cache', 'data/processed/llm_cache.jsonl')
    cache_path = Path(root) / cache_rel
    p_hash = prompt_signature(aspects)

    selected = select_reviews(list(reviews), cfg, review_ids)
    cache = load_cache(cache_path, aspects, model, p_hash)

    results = []
    api_key = None

    for row in selected:
        rid = row['review_id']
        comments = row.get('comments', '')
        if not isinstance(comments, str) or not clean_comment(comments):
            raise ValueError(f'Review {rid} has empty comments')
        t_hash = comment_sha256(comments)
        key = _cache_key(rid, t_hash, model, p_hash)

        if key in cache:
            results.append(cache[key])
            continue

        if api_key is None:
            api_key = os.environ.get('GEMINI_API_KEY', '').strip()
            if not api_key:
                raise RuntimeError('GEMINI_API_KEY is not set in environment and cache missed for review ' + rid)

        prompt = build_prompt(comments, aspects)
        last_error = None
        validated = None

        for attempt in range(1, retries + 1):
            try:
                raw_response = call_gemini_api(prompt, model, api_key)
                cleaned_json = strip_code_fences(raw_response)
                parsed = json.loads(cleaned_json)
                validated = validate(parsed, aspects)
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(min(2.0 ** (attempt - 1), 8.0))

        if validated is None:
            raise RuntimeError(
                f'LLM analysis failed for review_id {rid} after {retries} attempts: {last_error}'
            ) from last_error

        cache_entry = {
            'review_id': rid,
            'text_sha256': t_hash,
            'model': model,
            'prompt_version': PROMPT_VERSION,
            'prompt_sha256': p_hash,
            'aspects': aspects,
            **validated,
            'source': model,
        }
        append_cache(cache_path, cache_entry)
        result_row = {
            'review_id': rid,
            **validated,
            'source': model,
        }
        cache[key] = result_row
        results.append(result_row)

    return results


def estimate_cost(reviews, cfg, full_dataset_size: int = 5000) -> dict:
    """Ước tính số token và chi phí API (USD) cho mẫu LLM và toàn bộ tập dữ liệu."""
    llm_cfg = cfg.get('llm', {})
    model = llm_cfg.get('model', 'gemini-2.5-flash')
    aspects = list(llm_cfg.get('aspects') or [])
    sample_size = int(llm_cfg.get('sample_size', 1000))

    reviews_list = list(reviews)
    if reviews_list:
        avg_chars = sum(len(clean_comment(r.get('comments', ''))) for r in reviews_list) / len(reviews_list)
    else:
        avg_chars = 320.0

    prompt_overhead_chars = len(build_prompt('', aspects))
    avg_input_tokens = (prompt_overhead_chars + avg_chars) / 4.0
    avg_output_tokens = 45.0

    # Đơn giá tham khảo chuẩn của Gemini 2.5 Flash (USD / 1M tokens)
    input_price_per_m = 0.15
    output_price_per_m = 0.60

    def _cost_for_n(n: int) -> dict:
        in_tok = int(round(n * avg_input_tokens))
        out_tok = int(round(n * avg_output_tokens))
        usd = (in_tok / 1_000_000) * input_price_per_m + (out_tok / 1_000_000) * output_price_per_m
        return {
            'review_count': n,
            'estimated_input_tokens': in_tok,
            'estimated_output_tokens': out_tok,
            'estimated_cost_usd': round(usd, 6),
        }

    return {
        'model': model,
        'avg_review_chars': round(avg_chars, 1),
        'avg_input_tokens_per_review': round(avg_input_tokens, 1),
        'avg_output_tokens_per_review': avg_output_tokens,
        'input_price_per_1m_usd': input_price_per_m,
        'output_price_per_1m_usd': output_price_per_m,
        'sample_estimate': _cost_for_n(sample_size),
        'full_assigned_estimate': _cost_for_n(full_dataset_size),
    }
