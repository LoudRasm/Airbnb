"""TV5 — Phan Ngọc Huy. Biểu đồ SVG cho phân tích review, khía cạnh và đánh giá LLM vs Baseline.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .review_kpi import _parse_aspect_list

OWNER = 'TV5 — Phan Ngọc Huy'
IMPLEMENTED = True
READY = False  # Chỉ bật True sau khi triển khai, có test và review.

FONT = 'Segoe UI, Inter, Arial, sans-serif'
COLORS = {
    'ink': '#0f172a',
    'muted': '#475569',
    'line': '#cbd5e1',
    'panel': '#f8fafc',
    'bg': '#ffffff',
    'positive': '#0f766e',
    'mixed': '#d97706',
    'negative': '#b91c1c',
    'accent': '#1d4ed8',
    'baseline': '#64748b',
}


def _canvas(width: int, height: int, title: str, subtitle: str):
    root = ET.Element(
        'svg',
        xmlns='http://www.w3.org/2000/svg',
        width=str(width),
        height=str(height),
        viewBox=f'0 0 {width} {height}',
        role='img',
    )
    ET.SubElement(root, 'title').text = title
    ET.SubElement(root, 'rect', x='0', y='0', width=str(width), height=str(height), fill=COLORS['bg'])
    _text(root, 44, 40, title, size=19, weight='700')
    _text(root, 44, 64, subtitle, size=12, fill=COLORS['muted'])
    return root


def _text(parent, x, y, value, size=12, weight='400', fill=COLORS['ink'], anchor='start'):
    node = ET.SubElement(
        parent,
        'text',
        x=str(x),
        y=str(y),
        fill=fill,
        attrib={
            'font-family': FONT,
            'font-size': str(size),
            'font-weight': weight,
            'text-anchor': anchor,
        },
    )
    node.text = str(value)
    return node


def _save(root, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root)
    path.write_text(ET.tostring(root, encoding='unicode') + '\n', encoding='utf-8')
    return path


def _select_predictions(tables: dict) -> tuple[list[dict], str]:
    llm_rows = list(tables.get('llm_reviews') or [])
    if llm_rows:
        return llm_rows, 'Mẫu LLM được giao (Assigned LLM Sample)'
    base_rows = list(tables.get('baseline') or [])
    if base_rows:
        return base_rows, 'Tập review được giao chạy Baseline'
    return [], 'Chưa có dữ liệu dự đoán review'


def _render_sentiment_distribution(preds: list[dict], scope_label: str, city: str) -> ET.Element:
    sample_n = len(preds)
    counts = Counter(str(r.get('sentiment', '')) for r in preds)
    issue_n = counts['mixed'] + counts['negative']
    issue_pct = f'{(issue_n / sample_n) * 100:.1f}%' if sample_n else 'N/A'

    svg = _canvas(
        860,
        430,
        f'Phân bố cảm xúc (Sentiment) & Guest Issue Rate — {city}',
        f'Phạm vi: {scope_label} · n = {sample_n} reviews · Guest Issue Rate (Mixed + Negative) = {issue_pct} ({issue_n}/{sample_n})',
    )

    if sample_n == 0:
        _text(svg, 44, 140, 'Không có bản ghi dự đoán để hiển thị phân bố cảm xúc.', size=14, fill=COLORS['muted'])
        return svg

    left, right, top = 160, 740, 115
    bar_w = right - left
    categories = [
        ('positive', 'Positive (Tích cực)', COLORS['positive']),
        ('mixed', 'Mixed (Khen & Chê)', COLORS['mixed']),
        ('negative', 'Negative (Tiêu cực)', COLORS['negative']),
    ]

    for idx, (key, label, color) in enumerate(categories):
        y = top + idx * 78
        c = counts[key]
        ratio = c / sample_n if sample_n else 0.0
        width = max(int(round(bar_w * ratio)), 2 if c > 0 else 0)
        group = ET.SubElement(
            svg,
            'g',
            attrib={
                'data-sentiment': key,
                'data-count': str(c),
                'data-sample-n': str(sample_n),
            },
        )
        _text(group, left - 14, y + 24, label, size=13, weight='600', anchor='end')
        ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(bar_w), height='36', rx='6', fill=COLORS['panel'], stroke=COLORS['line'])
        if width > 0:
            ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(width), height='36', rx='6', fill=color)
        _text(group, left + width + 10, y + 24, f'{c}/{sample_n} ({ratio * 100:.1f}%)', size=12, weight='600')

    _text(
        svg,
        44,
        395,
        f'Chú thích: Mỗi review_id duy nhất tính 1 lần (n = {sample_n}). KPI 7 Guest Experience Issue Rate = (Mixed + Negative) / n = {issue_pct}.',
        size=11,
        fill=COLORS['muted'],
    )
    return svg


def _render_negative_aspects(preds: list[dict], scope_label: str, city: str, aspects: list[str]) -> ET.Element:
    sample_n = len(preds)
    neg_counts = Counter()
    pos_counts = Counter()
    for row in preds:
        for asp in set(_parse_aspect_list(row.get('negative_aspects'))):
            neg_counts[asp] += 1
        for asp in set(_parse_aspect_list(row.get('positive_aspects'))):
            pos_counts[asp] += 1

    ordered = sorted(aspects, key=lambda a: (-neg_counts[a], -pos_counts[a], a))
    max_neg = max([neg_counts[a] for a in ordered] + [1])

    height = max(440, 140 + len(ordered) * 40)
    svg = _canvas(
        860,
        height,
        f'Các khía cạnh bị phàn nàn nhiều nhất (Negative Aspects) — {city}',
        f'Phạm vi: {scope_label} · n = {sample_n} reviews · Đếm số review phàn nàn trên từng khía cạnh taxonomy',
    )

    if sample_n == 0 or not ordered:
        _text(svg, 44, 140, 'Không có dữ liệu khía cạnh để hiển thị.', size=14, fill=COLORS['muted'])
        return svg

    left, right, top = 160, 680, 105
    bar_w = right - left

    for idx, aspect in enumerate(ordered):
        y = top + idx * 38
        nc = neg_counts[aspect]
        pc = pos_counts[aspect]
        rate = nc / sample_n if sample_n else 0.0
        width = int(round((nc / max_neg) * bar_w)) if nc > 0 else 0
        group = ET.SubElement(
            svg,
            'g',
            attrib={
                'data-aspect': aspect,
                'data-negative-count': str(nc),
                'data-positive-count': str(pc),
                'data-sample-n': str(sample_n),
            },
        )
        _text(group, left - 14, y + 18, aspect, size=12, weight='600', anchor='end')
        ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(bar_w), height='24', rx='4', fill=COLORS['panel'], stroke=COLORS['line'])
        if width > 0:
            ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(max(width, 4)), height='24', rx='4', fill=COLORS['negative'])
        _text(group, right + 12, y + 17, f'Chê: {nc} ({rate * 100:.1f}%) · Khen: {pc}', size=11, fill=COLORS['ink'])

    _text(
        svg,
        44,
        height - 24,
        f'Chú thích: Một review có thể đề cập nhiều khía cạnh trong {len(ordered)} nhóm chuẩn hóa; mẫu số chung n = {sample_n}.',
        size=11,
        fill=COLORS['muted'],
    )
    return svg


def _render_sentiment_over_time(preds: list[dict], reviews_table: list[dict], scope_label: str, city: str) -> ET.Element:
    date_by_id = {
        str(r.get('review_id') or r.get('id') or '').strip(): str(r.get('date') or '').strip()
        for r in (reviews_table or [])
    }
    period_totals = Counter()
    period_issues = Counter()
    paired_dates = 0

    for row in preds:
        rid = str(row.get('review_id') or '').strip()
        r_date = str(row.get('date') or date_by_id.get(rid, '')).strip()
        if len(r_date) >= 7 and r_date[:4].isdigit() and r_date[5:7].isdigit():
            year = r_date[:4]
            month = int(r_date[5:7])
            quarter = (month - 1) // 3 + 1
            period = f'{year}-Q{quarter}'
            period_totals[period] += 1
            if row.get('sentiment') in {'mixed', 'negative'}:
                period_issues[period] += 1
            paired_dates += 1

    periods = sorted(period_totals)[-8:]
    svg = _canvas(
        860,
        430,
        f'Xu hướng cảm xúc & tỷ lệ phản ánh vấn đề theo thời gian — {city}',
        f'Phạm vi: {scope_label} · Ghép ngày review n = {paired_dates}/{len(preds)} · 8 quý gần nhất',
    )

    if not periods:
        _text(svg, 44, 140, 'Chưa đủ thông tin ngày review để vẽ xu hướng theo quý.', size=14, fill=COLORS['muted'])
        return svg

    left, right, top, bottom = 80, 800, 110, 340
    chart_h = bottom - top
    slot = (right - left) / max(len(periods), 1)
    max_total = max(period_totals[p] for p in periods) or 1

    ET.SubElement(svg, 'line', x1=str(left), y1=str(bottom), x2=str(right), y2=str(bottom), stroke=COLORS['ink'])

    for idx, period in enumerate(periods):
        tot = period_totals[period]
        iss = period_issues[period]
        pos = tot - iss
        x = left + idx * slot + slot * 0.2
        w = max(slot * 0.6, 22)
        total_h = int(round((tot / max_total) * chart_h))
        iss_h = int(round((iss / max_total) * chart_h))
        pos_h = max(total_h - iss_h, 0)

        group = ET.SubElement(
            svg,
            'g',
            attrib={'data-period': period, 'data-total': str(tot), 'data-issues': str(iss)},
        )
        if pos_h > 0:
            ET.SubElement(group, 'rect', x=f'{x:.1f}', y=str(bottom - total_h), width=f'{w:.1f}', height=str(pos_h), fill=COLORS['positive'])
        if iss_h > 0:
            ET.SubElement(group, 'rect', x=f'{x:.1f}', y=str(bottom - iss_h), width=f'{w:.1f}', height=str(iss_h), fill=COLORS['mixed'])
        _text(group, x + w / 2, bottom - total_h - 8, f'{tot} (issue {iss})', size=10, weight='600', anchor='middle')
        _text(group, x + w / 2, bottom + 20, period, size=11, anchor='middle')

    _text(
        svg,
        44,
        395,
        'Chú thích: Cột xanh là số review Positive; phần cam là số review Mixed/Negative trong từng quý theo ngày đăng review.',
        size=11,
        fill=COLORS['muted'],
    )
    return svg


def _render_model_comparison(eval_rows: list[dict], city: str) -> ET.Element:
    paired_info = (
        f"paired_n = {eval_rows[0].get('paired_n')}/{eval_rows[0].get('manual_n')}"
        if eval_rows else 'Chưa có bảng evaluation'
    )
    svg = _canvas(
        860,
        420,
        f'So sánh hiệu năng phân loại: LLM vs Keyword Baseline — {city}',
        f'Đánh giá trên cùng tập review gán nhãn thủ công ({paired_info})',
    )

    if not eval_rows:
        _text(svg, 44, 140, 'Chưa có dữ liệu đánh giá (evaluation) để so sánh LLM và Baseline.', size=14, fill=COLORS['muted'])
        return svg

    left, right, top = 200, 720, 115
    bar_w = right - left

    for idx, row in enumerate(eval_rows):
        source = str(row.get('source', f'model_{idx}'))
        acc = float(row.get('accuracy') or 0.0)
        f1 = float(row.get('macro_f1') or 0.0)
        paired_n = row.get('paired_n', 0)
        manual_n = row.get('manual_n', 0)
        y_base = top + idx * 120
        color = COLORS['accent'] if source == 'llm' else COLORS['baseline']

        group = ET.SubElement(
            svg,
            'g',
            attrib={
                'data-source': source,
                'data-paired-n': str(paired_n),
                'data-accuracy': str(acc),
                'data-macro-f1': str(f1),
            },
        )
        _text(group, 44, y_base + 18, f'Mô hình: {source.upper()} (n={paired_n}/{manual_n})', size=13, weight='700')

        for m_idx, (m_name, m_val) in enumerate([('Accuracy', acc), ('Macro-F1', f1)]):
            y = y_base + 30 + m_idx * 36
            w = int(round(bar_w * max(0.0, min(1.0, m_val))))
            _text(group, left - 12, y + 18, m_name, size=12, weight='600', anchor='end')
            ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(bar_w), height='24', rx='4', fill=COLORS['panel'], stroke=COLORS['line'])
            if w > 0:
                ET.SubElement(group, 'rect', x=str(left), y=str(y), width=str(max(w, 4)), height='24', rx='4', fill=color)
            _text(group, left + w + 10, y + 17, f'{m_val * 100:.1f}% ({m_val:.4f})', size=11, weight='600')

    _text(
        svg,
        44,
        390,
        'Chú thích: Cả LLM và Keyword Baseline được chấm trên đúng cùng tập review_id gán nhãn tay.',
        size=11,
        fill=COLORS['muted'],
    )
    return svg


def render(tables, figures, cfg):
    """Vẽ bộ biểu đồ SVG của TV5 vào thư mục figures; trả list[Path]."""
    tables = tables or {}
    figures_dir = Path(figures)
    city = str((cfg or {}).get('city', 'Toronto')).title()
    aspects = list((cfg or {}).get('llm', {}).get('aspects') or [
        'location', 'cleanliness', 'host', 'value', 'amenities', 'noise', 'safety', 'check-in'
    ])

    preds, scope_label = _select_predictions(tables)
    reviews_table = list(tables.get('reviews') or [])
    eval_rows = list(tables.get('evaluation') or [])

    paths = [
        _save(
            _render_sentiment_distribution(preds, scope_label, city),
            figures_dir / 'tv5_sentiment_distribution.svg',
        ),
        _save(
            _render_negative_aspects(preds, scope_label, city, aspects),
            figures_dir / 'tv5_negative_aspects.svg',
        ),
        _save(
            _render_sentiment_over_time(preds, reviews_table, scope_label, city),
            figures_dir / 'tv5_sentiment_over_time.svg',
        ),
        _save(
            _render_model_comparison(eval_rows, city),
            figures_dir / 'tv5_model_comparison.svg',
        ),
    ]
    return paths
