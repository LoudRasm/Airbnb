"""TV5 — Phan Ngọc Huy. Đánh giá LLM và Baseline trên tập nhãn thủ công.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
from .llm import SENTIMENTS
from .reviews import is_digit_id

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = True  # Integration validated; see docs/VERIFICATION.md.

EVALUATION_FIELDS = ['source', 'paired_n', 'manual_n', 'accuracy', 'macro_f1', 'meets_100_paired']
CLASS_ORDER = ('positive', 'mixed', 'negative')


def _index_records(records, kind: str) -> dict[str, str]:
    indexed = {}
    for row in records:
        if not isinstance(row, dict):
            raise ValueError(f'{kind} entry must be a dict')
        raw_id = row.get('review_id') if 'review_id' in row and row.get('review_id') not in (None, '') else row.get('id')
        rid = str(raw_id).strip() if raw_id is not None else ''
        if not is_digit_id(rid):
            raise ValueError(f'{kind} has invalid review_id: {raw_id!r}')
        if rid in indexed:
            raise ValueError(f'Duplicate review_id in {kind}: {rid}')
        sentiment = row.get('sentiment')
        if not isinstance(sentiment, str) or sentiment not in SENTIMENTS:
            raise ValueError(f'Invalid sentiment in {kind} for review_id {rid}: {sentiment!r}')
        indexed[rid] = sentiment
    return indexed


def evaluate_detailed(predictions, labels, source: str) -> dict:
    """Tính toán chi tiết Accuracy, Macro-F1, per-class F1, ma trận nhầm lẫn và các ca đoán sai."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError('source must be a non-empty string')
    label_map = _index_records(labels, 'labels')
    if not label_map:
        raise ValueError('labels must not be empty')
    pred_map = _index_records(predictions, 'predictions')

    missing_ids = sorted(set(label_map) - set(pred_map), key=int)
    if missing_ids:
        raise ValueError(
            f'Missing predictions for {len(missing_ids)} labeled reviews (first: {missing_ids[0]})'
        )

    ordered_ids = sorted(label_map, key=int)
    manual_n = len(ordered_ids)
    paired_n = manual_n

    confusion = {gold: {pred: 0 for pred in CLASS_ORDER} for gold in CLASS_ORDER}
    errors = []
    correct = 0

    for rid in ordered_ids:
        gold = label_map[rid]
        pred = pred_map[rid]
        confusion[gold][pred] += 1
        if gold == pred:
            correct += 1
        else:
            errors.append({'review_id': rid, 'gold': gold, 'predicted': pred})

    accuracy = round(correct / paired_n, 6)

    per_class = {}
    active_f1s = []
    for cls in CLASS_ORDER:
        tp = confusion[cls][cls]
        fp = sum(confusion[g][cls] for g in CLASS_ORDER if g != cls)
        fn = sum(confusion[cls][p] for p in CLASS_ORDER if p != cls)
        support = tp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        denom = 2 * tp + fp + fn
        f1 = (2 * tp) / denom if denom > 0 else 0.0
        per_class[cls] = {
            'precision': round(precision, 6),
            'recall': round(recall, 6),
            'f1': round(f1, 6),
            'support': support,
        }
        if denom > 0:
            active_f1s.append(f1)

    macro_f1 = round(sum(active_f1s) / len(active_f1s), 6) if active_f1s else 0.0

    summary = {
        'source': source.strip(),
        'paired_n': paired_n,
        'manual_n': manual_n,
        'accuracy': accuracy,
        'macro_f1': macro_f1,
        'meets_100_paired': paired_n >= 100,
    }
    return {
        'summary': summary,
        'per_class': per_class,
        'confusion_matrix': confusion,
        'errors': errors,
    }


def evaluate(predictions, labels, source):
    """Trả list[dict] đúng schema evaluation.csv:
    source, paired_n, manual_n, accuracy, macro_f1, meets_100_paired.
    """
    detailed = evaluate_detailed(predictions, labels, source)
    return [detailed['summary']]
