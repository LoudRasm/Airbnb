"""TV2 — Mai Anh Đức: hình QA (số dòng bị ảnh hưởng, thiếu dữ liệu, drift, tác động lên KPI).

Chỉ dùng thư viện chuẩn: mỗi hình là một file SVG viết tay, mở được bằng trình duyệt và chèn
được vào báo cáo. Số liệu lấy từ các bảng trong `tables` (xem docs/CONTRACTS.md):
- qa_report: số dòng bị ảnh hưởng theo rule, rows_after, median giá trước/sau;
- listings : bảng đã làm sạch, dùng đo tỷ lệ thiếu và cơ cấu room_type.
Hàm render không sửa bảng đầu vào và không đọc/ghi gì ngoài thư mục `figures`.

Ba hình (tên file cố định, để không ghi đè hình của người khác):
- qa_rules.svg            : ma trận rule × snapshot, mỗi ô là affected_rows;
- qa_missingness_drift.svg: tỷ lệ thiếu theo cột × snapshot và cơ cấu room_type (category drift);
- qa_kpi_impact.svg       : supply và median giá (CAD) trước/sau QA theo snapshot.
"""
from math import ceil, floor, log10
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

from . import qa

OWNER = 'TV2 — Mai Anh Đức'
READY = True
FIGURES = ('qa_rules.svg', 'qa_missingness_drift.svg', 'qa_kpi_impact.svg')

# Màu: bảng tham chiếu của dataviz skill (xanh tuần tự 100→700, nhóm phân loại theo thứ tự cố định).
SURFACE, INK, INK_2, INK_3, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#6b6a66', '#e3e2dd'
ZERO_FILL = '#efeeea'
RAMP = ('#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5',
        '#2a78d6', '#256abf', '#1c5cab', '#184f95', '#104281', '#0d366b')
CATEGORY_COLORS = ('#2a78d6', '#eb6834', '#1baf7a', '#eda100')  # blue, orange, aqua, yellow
OTHER_COLOR = '#8a8985'
BEFORE_COLOR, AFTER_COLOR = '#86b6ef', '#2a78d6'
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"

# Thứ tự rule hiển thị: 14 rule của clean_listings (bỏ raw_input) + rule so sánh chéo/schema/tham chiếu.
RULES_SHOWN = tuple(r for r in qa.RULE_ORDER if r != 'raw_input') + qa.CROSS_RULES + (qa.SCHEMA_RULE, qa.REFERENCE_RULE)
MISSING_COLUMNS = ('host_id', 'price', 'room_type', 'analysis_area', 'neighbourhood_cleansed', 'latitude', 'longitude')


# ---------- SVG cơ bản ----------

def _hex_rgb(color):
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def _luminance(color):
    channels = []
    for value in _hex_rgb(color):
        c = value / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _ink_on(fill):
    """Chữ trắng hoặc đen tùy nền, chọn bên có tương phản cao hơn."""
    lum = _luminance(fill)
    return '#ffffff' if (1.05 / (lum + 0.05)) > ((lum + 0.05) / 0.053) else INK


def _ramp(t):
    """t trong [0, 1] -> màu trên thang xanh tuần tự (nội suy giữa các bậc)."""
    t = min(1.0, max(0.0, t)) * (len(RAMP) - 1)
    low = int(t)
    high = min(low + 1, len(RAMP) - 1)
    a, b = _hex_rgb(RAMP[low]), _hex_rgb(RAMP[high])
    mixed = tuple(round(a[i] + (b[i] - a[i]) * (t - low)) for i in range(3))
    return '#%02x%02x%02x' % mixed


def _text(x, y, content, size=12, fill=INK, anchor='start', weight='400'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{escape(str(content))}</text>')


def _rect(x, y, w, h, fill, stroke=None, rx=0, width=2):
    edge = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{edge}/>'


def _line(x1, y1, x2, y2, color=GRID):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>'


def _paragraph(x, y, text, width_chars, size=12, fill=INK_2, line_height=17):
    lines = wrap(text, width_chars)
    return ''.join(_text(x, y + i * line_height, line, size, fill) for i, line in enumerate(lines)), len(lines) * line_height


def _svg(width, height, title, description, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-labelledby="t d" font-family="{FONT}">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(description)}</desc>'
            f'{_rect(0, 0, width, height, SURFACE)}{body}</svg>\n')


def _heading(title, subtitle):
    return _text(24, 32, title, 18, INK, weight='600') + _text(24, 54, subtitle, 13, INK_2)


def _legend_swatch(x, y, fill, label):
    return _rect(x, y - 11, 14, 14, fill, rx=3) + _text(x + 20, y, label, 12, INK_2)


# ---------- Tính số liệu từ các bảng (hàm thuần) ----------

def _number(value):
    if value is None or value == '':
        return None
    return float(value)


def _blank(value):
    return value is None or str(value).strip() == ''


def rule_matrix(qa_report, snapshots):
    """{(snapshot, rule): affected_rows} cho các rule hiển thị; rule không có dòng thì không có khóa."""
    shown, matrix = set(RULES_SHOWN), {}
    for row in qa_report:
        key = (row['snapshot_date'], row['rule'])
        if row['rule'] in shown and row['snapshot_date'] in snapshots and key not in matrix:
            matrix[key] = int(row['affected_rows'])
    return matrix


def missing_rates(listings, snapshots, columns=MISSING_COLUMNS):
    """{(snapshot, cột): tỷ lệ dòng rỗng}; mốc không có dòng nào thì bỏ qua."""
    rates = {}
    for snapshot in snapshots:
        rows = [r for r in listings if r['snapshot_date'] == snapshot]
        if not rows:
            continue
        for column in columns:
            rates[(snapshot, column)] = sum(_blank(r.get(column)) for r in rows) / len(rows)
    return rates


def room_type_shares(listings, snapshots, room_types):
    """({snapshot: [(nhãn, tỷ lệ), ...]}, [nhãn theo thứ tự]); room_type ngoài danh sách gộp thành 'Khác / rỗng'.

    Danh sách nhãn chung cho mọi snapshot nên các cột của hình cùng một bộ màu, cùng thứ tự.
    """
    other = 'Khác / rỗng'
    known = list(room_types)
    rows_by_snapshot = {s: [r for r in listings if r['snapshot_date'] == s] for s in snapshots}
    rows_by_snapshot = {s: rows for s, rows in rows_by_snapshot.items() if rows}
    has_other = any(r.get('room_type') not in known for rows in rows_by_snapshot.values() for r in rows)
    labels = known + ([other] if has_other else [])
    out = {}
    for snapshot, rows in rows_by_snapshot.items():
        counts = {}
        for r in rows:
            name = r.get('room_type') if r.get('room_type') in known else other
            counts[name] = counts.get(name, 0) + 1
        out[snapshot] = [(name, counts.get(name, 0) / len(rows)) for name in labels]
    return out, labels


def kpi_pairs(qa_report, snapshots):
    """Mỗi snapshot: supply và median giá trước (raw_input) / sau (rule cuối của clean_listings) QA."""
    clean_rules, pairs = set(qa.RULE_ORDER), {}
    for snapshot in snapshots:
        rows = [r for r in qa_report if r['snapshot_date'] == snapshot and r['rule'] in clean_rules]
        base = next((r for r in rows if r['rule'] == 'raw_input'), None)
        if base is None:
            continue
        last = rows[-1]
        pairs[snapshot] = {'supply_before': int(base['rows_after']), 'supply_after': int(last['rows_after']),
                           'median_before': _number(base['median_price_after']),
                           'median_after': _number(last['median_price_after'])}
    return pairs


def snapshot_sizes(qa_report, listings, snapshots):
    """n listing mỗi mốc trước QA: dòng raw_input của qa_report; không có thì đếm trong listings."""
    sizes = {}
    for snapshot in snapshots:
        raw = next((r for r in qa_report if r['snapshot_date'] == snapshot and r['rule'] == 'raw_input'), None)
        sizes[snapshot] = int(raw['affected_rows']) if raw else sum(r['snapshot_date'] == snapshot for r in listings)
    return sizes


def price_counts(listings, snapshots):
    """n listing có giá mỗi mốc: mẫu số của median giá."""
    return {s: sum(r['snapshot_date'] == s and not _blank(r.get('price')) for r in listings) for s in snapshots}


def headline_rules(matrix, sizes):
    """(tiêu đề nêu kết luận, ghi chú phụ) cho hình rule × mốc; số lấy từ chính ma trận."""
    clean = [r for r in RULES_SHOWN if r in qa.RULE_ORDER]
    totals = {r: sum(v for (_, rule), v in matrix.items() if rule == r) for r in clean}
    flagged, n_total = sum(totals.values()), sum(sizes.values())
    if flagged == 0:
        title = f'Không rule nào trong {len(clean)} rule của mỗi mốc tìm thấy dòng lỗi ({n_total:,} dòng)'
    else:
        top = max(totals, key=totals.get)
        title = f'QA gắn cờ {flagged:,}/{n_total:,} dòng ({flagged / max(n_total, 1) * 100:.1f}%), nhiều nhất ở {top}'
    cross = {r: sum(v for (_, rule), v in matrix.items() if rule == r) for r in qa.CROSS_RULES}
    cross = {r: v for r, v in cross.items() if v > 0}
    extra = ''
    if cross:
        top = max(cross, key=cross.get)
        extra = f' · giữa các mốc: {top} = {cross[top]:,} lượt'
    return title, extra


def headline_missingness(rates, shares):
    """Tiêu đề nêu kết luận cho hình thiếu dữ liệu + category drift."""
    columns = sorted({c for (_, c), v in rates.items() if v > 0})
    n_columns = len({c for _, c in rates})
    if columns:
        names = ', '.join(columns[:3]) + ('…' if len(columns) > 3 else '')
        left = f'Thiếu dữ liệu ở {len(columns)}/{n_columns} cột ({names})'
    else:
        left = 'Không cột nào thiếu dữ liệu'
    spread = 0.0
    for index in range(len(next(iter(shares.values()), []))):
        values = [rows[index][1] for rows in shares.values()]
        spread = max(spread, (max(values) - min(values)) * 100)
    right = ('cơ cấu room_type không đổi giữa các mốc' if spread < 0.05
             else f'tỷ trọng room_type lệch tối đa {spread:.1f} điểm % giữa các mốc')
    return f'{left}; {right}'


def headline_kpi(pairs):
    """(tiêu đề nêu kết luận, chênh lệch supply lớn nhất, chênh lệch median lớn nhất)."""
    supply = max((abs(p['supply_after'] - p['supply_before']) for p in pairs.values()), default=0)
    median = max((abs(p['median_after'] - p['median_before']) for p in pairs.values()
                  if p['median_after'] is not None and p['median_before'] is not None), default=0)
    if supply == 0 and median == 0:
        return 'QA không làm đổi KPI: supply và median giá giữ nguyên ở mọi mốc', supply, median
    return f'QA đổi supply tối đa {supply:,} listing và median giá tối đa {median:,.1f} CAD', supply, median


def _source_note(snapshots, sizes, context):
    """Nguồn, mốc chụp và giới hạn của cohort, ghi ngay trên hình."""
    where = ', '.join(x for x in (f'Inside Airbnb', (context or {}).get('city')) if x)
    group = (context or {}).get('group')
    cohort = f'{max(sizes.values(), default=0):,} listing' + (f' của nhóm {group}' if group else '')
    return (f'Nguồn: {where}; cohort {cohort}; mốc chụp {", ".join(snapshots)}. '
            f'Giới hạn: chỉ cohort này, không suy ra toàn thị trường.')


def _snapshot_header(x, y, snapshot, size_n, size=12):
    return _text(x, y - 15, snapshot, size, INK_2, 'middle', '600') + _text(x, y, f'n={size_n:,}', 11, INK_3, 'middle')


# ---------- Hình 1: ma trận rule × snapshot ----------

def figure_rules(qa_report, snapshots, sizes=None, context=None):
    matrix = rule_matrix(qa_report, snapshots)
    sizes = sizes or snapshot_sizes(qa_report, [], snapshots)
    title, cross_note = headline_rules(matrix, sizes)
    vmax = max([v for v in matrix.values()] + [1])
    left, group_x, cell_x, cell_w, cell_h, top = 24, 250, 410, 124, 24, 126
    width = cell_x + cell_w * len(snapshots) + 24
    body = [_heading(title, f'Mỗi ô: số dòng bị ảnh hưởng theo rule và mốc (đơn vị: listing){cross_note}')]
    body.append(_text(left, top - 10, 'Rule', 12, INK_2, weight='600'))
    body.append(_text(group_x, top - 10, 'Nhóm', 12, INK_2, weight='600'))
    for j, snapshot in enumerate(snapshots):
        body.append(_snapshot_header(cell_x + j * cell_w + cell_w / 2 - 1, top - 8, snapshot, sizes.get(snapshot, 0)))
    for i, rule in enumerate(RULES_SHOWN):
        y = top + i * (cell_h + 2)
        body.append(_text(left, y + 16, rule, 12, INK))
        body.append(_text(group_x, y + 16, qa.RULES[rule][0], 12, INK_3))
        for j, snapshot in enumerate(snapshots):
            x = cell_x + j * cell_w
            value = matrix.get((snapshot, rule))
            if value is None:
                body.append(_rect(x, y, cell_w - 2, cell_h, SURFACE, stroke=GRID, rx=3, width=1))
                body.append(_text(x + cell_w / 2 - 1, y + 16, '–', 13, INK_3, 'middle'))
            else:
                fill = ZERO_FILL if value == 0 else _ramp(0.12 + 0.88 * (value / vmax) ** 0.5)
                body.append(_rect(x, y, cell_w - 2, cell_h, fill, rx=3))
                body.append(_text(x + cell_w / 2 - 1, y + 16, f'{value:,}', 12,
                                  INK_3 if value == 0 else _ink_on(fill), 'middle', '400' if value == 0 else '600'))
    bottom = top + len(RULES_SHOWN) * (cell_h + 2) + 18
    body.append(_legend_swatch(left, bottom, ZERO_FILL, '0: rule đã chạy, không có dòng lỗi'))
    body.append(_legend_swatch(left + 300, bottom, _ramp(0.5), 'có dòng bị ảnh hưởng (đậm hơn = nhiều hơn)'))
    body.append(_legend_swatch(left + 640, bottom, SURFACE, '–: không chạy / không áp dụng'))
    ran = sum(1 for v in matrix.values() if v > 0)
    note = (f'Mỗi ô là affected_rows của rule trong qa_report (gắn cờ, đặt rỗng hoặc loại dòng tùy rule; xem '
            f'reports/qa_rule_catalog.csv). Rule so sánh chéo cần mốc trước đó; schema_drift và '
            f'neighbourhood_not_in_reference chạy sau khi đủ các snapshot nên có thể hiện –. '
            f'Có {ran} ô có dòng bị ảnh hưởng. ' + _source_note(snapshots, sizes, context))
    paragraph, used = _paragraph(left, bottom + 30, note, 118)
    body.append(paragraph)
    height = bottom + 30 + used + 16
    description = f'{title}. Ma trận {len(RULES_SHOWN)} rule × {len(snapshots)} snapshot; {ran} ô có dòng bị ảnh hưởng.'
    return _svg(width, height, title, description, ''.join(body))


# ---------- Hình 2: thiếu dữ liệu và category drift ----------

def figure_missingness_drift(listings, snapshots, room_types, sizes=None, context=None):
    rates = missing_rates(listings, snapshots)
    shares, labels = room_type_shares(listings, snapshots, room_types)
    sizes = sizes or snapshot_sizes([], listings, snapshots)
    title = headline_missingness(rates, shares)
    left, cell_x, cell_w, cell_h, top = 24, 214, 92, 32, 128
    width = 1000
    body = [_heading(title, 'Trái: tỷ lệ dòng rỗng theo cột (%) · Phải: cơ cấu room_type (% listing) · bảng đã làm sạch')]
    body.append(_text(left, top - 40, 'Tỷ lệ thiếu theo cột (%)', 14, INK, weight='600'))
    for j, snapshot in enumerate(snapshots):
        body.append(_snapshot_header(cell_x + j * cell_w + cell_w / 2 - 1, top - 8, snapshot, sizes.get(snapshot, 0), 11))
    for i, column in enumerate(MISSING_COLUMNS):
        y = top + i * (cell_h + 2)
        body.append(_text(left, y + 20, column, 12, INK))
        for j, snapshot in enumerate(snapshots):
            x = cell_x + j * cell_w
            rate = rates.get((snapshot, column))
            if rate is None:
                body.append(_rect(x, y, cell_w - 2, cell_h, SURFACE, stroke=GRID, rx=3, width=1))
                body.append(_text(x + cell_w / 2 - 1, y + 20, '–', 13, INK_3, 'middle'))
                continue
            fill = ZERO_FILL if rate == 0 else _ramp(0.12 + 0.88 * rate)
            label = '0%' if rate == 0 else ('100%' if rate == 1 else f'{rate * 100:.1f}%')
            body.append(_rect(x, y, cell_w - 2, cell_h, fill, rx=3))
            body.append(_text(x + cell_w / 2 - 1, y + 20, label, 12, INK_3 if rate == 0 else _ink_on(fill),
                              'middle', '400' if rate == 0 else '600'))
    grid_bottom = top + len(MISSING_COLUMNS) * (cell_h + 2)

    px, py, ph, bar_w, gap = 700, top, grid_bottom - top - 2, 58, 14
    body.append(_text(px - 40, top - 40, 'Cơ cấu room_type (% listing)', 14, INK, weight='600'))
    for tick in (0, 50, 100):
        y = py + ph - ph * tick / 100
        body.append(_line(px, y, px + len(snapshots) * (bar_w + gap) - gap + 8, y))
        body.append(_text(px - 8, y + 4, f'{tick}%', 11, INK_3, 'end'))
    colors = {name: (CATEGORY_COLORS[i] if i < len(CATEGORY_COLORS) else OTHER_COLOR) for i, name in enumerate(labels)}
    colors['Khác / rỗng'] = OTHER_COLOR
    for j, snapshot in enumerate(snapshots):
        x = px + 8 + j * (bar_w + gap)
        base = py + ph
        for name, share in shares.get(snapshot, []):
            height = ph * share
            if height <= 0:
                continue
            base -= height
            body.append(_rect(x, base, bar_w, height, colors[name], stroke=SURFACE))
            if share >= 0.08:
                body.append(_text(x + bar_w / 2, base + height / 2 + 4, f'{share * 100:.1f}%', 11,
                                  _ink_on(colors[name]), 'middle', '600'))
        body.append(_text(x + bar_w / 2, py + ph + 18, snapshot, 10, INK_2, 'middle'))
    legend_y = grid_bottom + 48
    for k, name in enumerate(labels):
        body.append(_legend_swatch(px - 40 + (k % 2) * 160, legend_y + (k // 2) * 20, colors[name], name))
    note = ('Thiếu = giá trị rỗng/None trong bảng listings đã làm sạch. price rỗng ở mốc không phải mốc cuối không bị '
            'coi là lỗi vì giá chỉ phân tích ở mốc cuối; mốc cuối là price_missing_final. Cơ cấu room_type đổi giữa '
            'các snapshot là dấu hiệu category drift (rule room_type_unknown, cross_category_changed). '
            + _source_note(snapshots, sizes, context))
    paragraph, used = _paragraph(left, legend_y + 46, note, 150)
    body.append(paragraph)
    height = legend_y + 46 + used + 16
    worst = max(rates.items(), key=lambda kv: kv[1], default=(None, 0))
    description = (f'{title}. Tỷ lệ thiếu theo cột × snapshot và cơ cấu room_type; tỷ lệ thiếu cao nhất '
                   f'{worst[1] * 100:.1f}% ở cột {worst[0][1] if worst[0] else "-"}.')
    return _svg(width, height, title, description, ''.join(body))


# ---------- Hình 3: tác động QA lên KPI ----------

def _axis(value):
    """(giá trị lớn nhất của trục, bước vạch) với vạch tròn (1, 2, 2.5, 5 × 10^k), tối đa khoảng 5 khoảng."""
    if value <= 0:
        return 1, 1
    raw = value / 5
    magnitude = 10 ** floor(log10(raw))
    step = next(m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw)
    return step * ceil(value / step), step


def _bar_panel(x0, y0, w, h, title, unit, snapshots, pairs, key, fmt, label_fmt=None, counts=None, count_label='n'):
    """Một panel cột ghép: trước/sau QA cho mỗi snapshot, trục y bắt đầu từ 0."""
    values = [pairs[s][f'{key}_{side}'] for s in snapshots if s in pairs for side in ('before', 'after')]
    top_value, step = _axis(max([v for v in values if v is not None] + [0]) * 1.1)
    ticks = round(top_value / step)
    plot_x, plot_w = x0 + 56, w - 66
    label_fmt = label_fmt or fmt
    out = [_text(x0, y0 - 28, title, 14, INK, weight='600'), _text(x0, y0 - 10, unit, 11, INK_3)]
    for tick in range(ticks + 1):
        value = step * tick
        y = y0 + h - h * value / top_value
        out.append(_line(plot_x, y, plot_x + plot_w, y))
        out.append(_text(plot_x - 8, y + 4, fmt(value), 11, INK_3, 'end'))
    group_w = plot_w / len(snapshots)
    bar_w = min(30, group_w / 3)
    for j, snapshot in enumerate(snapshots):
        cx = plot_x + group_w * (j + 0.5)
        out.append(_text(cx, y0 + h + 18, snapshot, 11, INK_2, 'middle'))
        if counts is not None:
            out.append(_text(cx, y0 + h + 33, f'{count_label}={counts.get(snapshot, 0):,}', 10, INK_3, 'middle'))
        for side, color, dx in (('before', BEFORE_COLOR, -bar_w - 1), ('after', AFTER_COLOR, 1)):
            value = pairs.get(snapshot, {}).get(f'{key}_{side}')
            if value is None:
                out.append(_text(cx + dx + bar_w / 2, y0 + h - 6, 'n/a', 10, INK_3, 'middle'))
                continue
            height = h * value / top_value
            out.append(_rect(cx + dx, y0 + h - height, bar_w, height, color, rx=3))
            out.append(_text(cx + dx + bar_w / 2, y0 + h - height - 5, label_fmt(value), 10, INK_2, 'middle'))
    return ''.join(out)


def figure_kpi_impact(qa_report, snapshots, listings=(), sizes=None, context=None):
    pairs = kpi_pairs(qa_report, snapshots)
    sizes = sizes or snapshot_sizes(qa_report, listings, snapshots)
    title, supply_delta, median_delta = headline_kpi(pairs)
    width, panel_h, top = 980, 220, 134
    body = [_heading(title, 'Cột nhạt: trước QA (raw_input) · cột đậm: sau QA (rule cuối) · theo snapshot')]
    body.append(_bar_panel(24, top, 440, panel_h, 'Supply (số listing)', 'listing', snapshots, pairs,
                           'supply', lambda v: f'{v:,.0f}', counts=sizes, count_label='n'))
    body.append(_bar_panel(520, top, 440, panel_h, 'Median giá', 'CAD / đêm; n/a = không có giá', snapshots, pairs,
                           'median', lambda v: f'{v:,.0f}', lambda v: f'{v:,.1f}',
                           counts=price_counts(listings, snapshots), count_label='n có giá'))
    legend_y = top + panel_h + 58
    body.append(_legend_swatch(24, legend_y, BEFORE_COLOR, 'Trước QA'))
    body.append(_legend_swatch(130, legend_y, AFTER_COLOR, 'Sau QA'))
    note = (f'Chênh lệch lớn nhất sau QA: supply {supply_delta:,} listing, median giá {median_delta:,.2f} CAD. '
            'Median tính trên các dòng có giá (n có giá); trục y bắt đầu từ 0. Theo contract giá chỉ dùng phân tích '
            'ở mốc cuối, các mốc trước hiển thị để kiểm chứng QA. ' + _source_note(snapshots, sizes, context))
    paragraph, used = _paragraph(24, legend_y + 30, note, 140)
    body.append(paragraph)
    height = legend_y + 30 + used + 16
    description = f'{title}. Chênh lệch supply tối đa {supply_delta}, median {median_delta:.2f} CAD.'
    return _svg(width, height, title, description, ''.join(body))


# ---------- Điểm vào của pipeline ----------

def render(tables, figures, cfg):
    """Đọc các bảng từ tables, lưu hình trong figures, trả list[Path].

    tables xem docs/CONTRACTS.md; figures là Path đã tạo; không sửa bảng đầu vào.
    """
    missing = [name for name in ('qa_report', 'listings') if name not in tables]
    if missing:
        raise ValueError(f'viz_qa cần các bảng {missing} trong tables')
    snapshots = list(cfg['snapshots'])
    room_types = cfg.get('qa', {}).get('room_types', ())
    figures = Path(figures)
    figures.mkdir(parents=True, exist_ok=True)
    sizes = snapshot_sizes(tables['qa_report'], tables['listings'], snapshots)
    context = {'city': str(cfg.get('city', '')).title(), 'group': cfg.get('assignment', {}).get('group')}
    contents = (figure_rules(tables['qa_report'], snapshots, sizes, context),
                figure_missingness_drift(tables['listings'], snapshots, room_types, sizes, context),
                figure_kpi_impact(tables['qa_report'], snapshots, tables['listings'], sizes, context))
    paths = []
    for name, svg in zip(FIGURES, contents):
        path = figures / name
        path.write_text(svg, encoding='utf-8', newline='\n')
        paths.append(path)
    return paths
