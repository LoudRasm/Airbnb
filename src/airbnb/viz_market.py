"""TV1: dependency-free SVG charts for cohort coverage and reported host-ID changes."""
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from . import analysis

OWNER = 'TV1 — Dương Nhật Huy'
IMPLEMENTED = True
READY = False  # Code and figures verified; pending the team's peer-review gate.
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def _add(parent, tag, text=None, **attrs):
    element = ET.SubElement(parent, f'{{{NS}}}{tag}', {key.replace('_', '-'): str(value)
                                                      for key, value in attrs.items()})
    element.text = text
    return element


def _text(parent, x, y, text, size=14, **attrs):
    return _add(parent, 'text', text, x=x, y=y, font_size=size, fill='#24364b', **attrs)


def _canvas(title, subtitle, ceiling, percent=False):
    svg = ET.Element(f'{{{NS}}}svg', {'width': '1040', 'height': '650', 'viewBox': '0 0 1040 650',
                                    'role': 'img', 'font-family': 'Arial, DejaVu Sans, sans-serif'})
    _add(svg, 'title', title)
    _add(svg, 'desc', subtitle + ' Chỉ phản ánh cohort listing được giao, không phải toàn Toronto.')
    _add(svg, 'rect', x=0, y=0, width=1040, height=650, fill='#ffffff')
    _text(svg, 52, 43, title, 24, font_weight=700)
    _text(svg, 52, 74, subtitle, 14)
    for index in range(5):
        value = ceiling * index / 4
        y = 470 - 320 * index / 4
        _add(svg, 'line', x1=100, x2=990, y1=y, y2=y, stroke='#e1e7ed')
        label = f'{value:.1%}' if percent else f'{value:,.0f}'
        _text(svg, 85, y + 5, label, 13, text_anchor='end')
    return svg


def _write(path, svg):
    ET.ElementTree(svg).write(path, encoding='utf-8', xml_declaration=True)
    return path


def render(tables, figures, cfg):
    """Save two SVGs, return list[Path]; never mutate tables or call data/network APIs.

    Uses cohort_summary/churn_kpi tables. A fallback derives them only from supplied listings.
    """
    figures = Path(figures)
    summaries = tables.get('cohort_summary')
    transitions = tables.get('churn_kpi')
    if summaries is None:
        summaries = analysis.cohort_summary(tables['listings'], cfg['snapshots'])
    if transitions is None:
        transitions = analysis.churn(tables['listings'], cfg['snapshots'])
    summaries, transitions = list(summaries), list(transitions)
    sizes = [max(row['cohort_size'], row['observed_listings']) for row in summaries]
    ceiling = max(1, math.ceil(max(sizes, default=0) / 100) * 100)
    svg = _canvas('Mức bao phủ cohort listing qua các mốc',
                  f'{cfg["city"].title()} · Số listing quan sát / số ID trong cohort', ceiling)
    _add(svg, 'rect', x=100, y=103, width=16, height=12, fill='#dfe6ee')
    _text(svg, 124, 114, 'Cohort', 13)
    _add(svg, 'rect', x=220, y=103, width=16, height=12, fill='#28628e')
    _text(svg, 244, 114, 'Quan sát được', 13)
    spacing = 890 / max(1, len(summaries))
    for index, row in enumerate(summaries):
        center = 100 + spacing * (index + 0.5)
        width = min(110, spacing * 0.55)
        group = _add(svg, 'g', data_snapshot=row['snapshot_date'],
                     data_observed=row['observed_listings'], data_cohort=row['cohort_size'])
        for count, color in [(row['cohort_size'], '#dfe6ee'), (row['observed_listings'], '#28628e')]:
            height = 320 * count / ceiling
            _add(group, 'rect', x=center-width/2, y=470-height, width=width, height=height, fill=color)
        _text(group, center, 458-320*max(row['cohort_size'], row['observed_listings'])/ceiling,
              f'{row["observed_listings"]:,} / {row["cohort_size"]:,}', 14, text_anchor='middle')
        _text(group, center, 503, row['snapshot_date'], 14, text_anchor='middle')
        coverage = 'N/A' if row['coverage'] is None else f'{row["coverage"]:.1%}'
        _text(group, center, 529, f'Bao phủ {coverage}', 13, text_anchor='middle')
    if not summaries:
        _text(svg, 545, 300, 'Chưa có dữ liệu cohort', 18, text_anchor='middle')
    basis = {row['cohort_basis'] for row in summaries}
    denominator = 'workbook phân công' if basis == {'assignment'} else 'hợp các ID quan sát; không phải mẫu số phân công'
    _text(svg, 52, 580, f'Mẫu số: {denominator}.', 13)
    _text(svg, 52, 607, 'Cohort cố định có thể bao phủ 100% ở mọi mốc; điều đó không chứng minh thị trường không thay đổi.', 13)
    figures.mkdir(parents=True, exist_ok=True)
    paths = [_write(figures / 'tv1_cohort_coverage.svg', svg)]

    rates = [row['host_change_rate'] for row in transitions if row['host_change_rate'] is not None]
    ceiling = max(0.01, math.ceil(max(rates, default=0) * 100) / 100)
    svg = _canvas('Thay đổi host_id trên cùng listing giữa hai mốc',
                  'Tỷ lệ trên các cặp listing có host_id hợp lệ ở cả hai mốc', ceiling, percent=True)
    spacing = 890 / max(1, len(transitions))
    for index, row in enumerate(transitions):
        center = 100 + spacing * (index + 0.5)
        rate = row['host_change_rate']
        group = _add(svg, 'g', data_previous=row['previous_snapshot'], data_snapshot=row['snapshot_date'],
                     data_changed=row['host_changed'], data_comparable=row['host_comparable'],
                     data_rate='NA' if rate is None else rate)
        height = 0 if rate is None else 320 * rate / ceiling
        if rate is not None:
            _add(group, 'rect', x=center-50, y=470-height, width=100, height=height, fill='#28628e')
        label = 'N/A' if rate is None else f'{rate:.1%}'
        _text(group, center, 440-height, label, 18, text_anchor='middle', font_weight=700)
        _text(group, center, 460-height, f'{row["host_changed"]} / {row["host_comparable"]} cặp', 13, text_anchor='middle')
        _text(group, center, 500, f'{row["previous_snapshot"]} →', 14, text_anchor='middle')
        _text(group, center, 523, row['snapshot_date'], 14, text_anchor='middle')
        _text(group, center, 548, f'Loại khỏi mẫu số: {row["host_pairs_excluded"]} cặp', 12, text_anchor='middle')
    if not transitions:
        _text(svg, 545, 300, 'Cần ít nhất hai mốc để so sánh', 18, text_anchor='middle')
    _text(svg, 52, 590, 'host_id đổi là thay đổi thuộc tính được ghi nhận; không chứng minh chuyển quyền sở hữu.', 13)
    _text(svg, 52, 617, 'Không dùng số ID mới/mất trong cohort để suy luận listing gia nhập/rời toàn thị trường Toronto.', 13)
    paths.append(_write(figures / 'tv1_host_changes.svg', svg))
    return paths
