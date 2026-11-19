"""TV2 — Mai Anh Đức: QA & preprocessing cho listings.

Module chỉ định nghĩa hàm/hằng số; không đọc file, không gọi API, không ghi kết quả.
Raw không bị sửa: mọi dòng đầu ra là bản sao đã chuẩn hóa.

Nguyên tắc:
- Ưu tiên gắn cờ (qa_flags); chỉ DROP khi dòng không dùng được làm khóa (thiếu/trùng ID).
- Giá lỗi/ngoại lai bị đặt None nhưng dòng vẫn ở lại để không làm sai supply.
- Giá rỗng ở mốc không phải mốc cuối KHÔNG phải lỗi (không cờ, không đếm).
- neighbourhood_cleansed thiếu không được điền bằng analysis_area.
- ID luôn là str chính xác, không đi qua float.
- Ngưỡng/hộp bao nằm trong cfg['qa'], không hard-code theo thành phố.
"""
from collections import Counter
from datetime import date
from math import asin, cos, isfinite, radians, sin, sqrt
from statistics import median

OWNER = 'TV2 — Mai Anh Đức'
READY = True  

# Cột listings cần có để tạo cleaned schema (id -> listing_id).
REQUIRED_COLUMNS = ('id', 'host_id', 'price', 'room_type', 'latitude', 'longitude',
                    'neighbourhood_cleansed', 'analysis_area')
DATE_COLUMNS = ('last_scraped', 'host_since', 'first_review', 'last_review')
# Cột dùng cho KPI/phân tích để đo mức độ thiếu (cfg['qa']['profile_columns'] ghi đè).
PROFILE_COLUMNS = ('id', 'host_id', 'price', 'room_type', 'property_type', 'accommodates',
                   'minimum_nights', 'availability_90', 'review_scores_rating',
                   'latitude', 'longitude', 'neighbourhood_cleansed', 'host_since',
                   'host_total_listings_count', 'last_scraped')
DEFAULTS = {'price_max': 10000, 'min_nights_cap': 365, 'max_scrape_lag_days': 3, 'coord_shift_km': 1.0}

RULE_ORDER = (
    'raw_input', 'id_missing', 'id_format', 'duplicate_key', 'critical_field_missing',
    'price_missing_final', 'price_unparseable', 'price_outlier', 'room_type_unknown',
    'coordinates_invalid', 'coordinates_outside_city', 'neighbourhood_missing',
    'min_nights_outlier', 'date_invalid', 'scrape_date_offset',
)
CROSS_RULES = ('cross_host_id_changed', 'cross_category_changed', 'cross_coordinates_moved')
SCHEMA_RULE = 'schema_drift'
REFERENCE_RULE = 'neighbourhood_not_in_reference'  # hàm riêng, không nằm trong clean_listings

# Name -> (nhóm, condition, reason, action). Là nguồn duy nhất cho docs/QA.md và test đối chiếu.
RULES = {
    'raw_input': ('Cơ sở', 'Mọi dòng listing đã lọc theo workbook', 'Mốc so sánh trước/sau; ghi cột bắt buộc bị thiếu', 'Không đổi dữ liệu'),
    'id_missing': ('Thiếu', 'id rỗng sau khi bỏ khoảng trắng', 'Không có khóa (snapshot_date, listing_id) thì không nối được các bảng', 'Loại dòng'),
    'id_format': ('Kiểu sai', 'id không phải toàn chữ số ASCII (vd 123.0, 1.2e+17)', 'Dấu hiệu ID đã đi qua float/Excel và mất chính xác', 'Gắn cờ, giữ nguyên chuỗi'),
    'duplicate_key': ('Trùng', 'Cùng listing_id xuất hiện nhiều lần trong một mốc', 'Khóa phải duy nhất; không đếm lặp supply', 'Giữ dòng đầu, loại dòng sau, đếm số cặp khác nội dung'),
    'critical_field_missing': ('Thiếu', 'host_id, room_type hoặc analysis_area rỗng', 'Cần cho KPI host nhiều listing, entire-home và theo vùng', 'Gắn cờ theo từng cột (host_id_missing, room_type_missing, analysis_area_missing)'),
    'price_missing_final': ('Thiếu', 'price rỗng ở mốc cuối của config', 'Giá chỉ phân tích ở mốc cuối; rỗng ở mốc trước không phải lỗi', 'Gắn cờ (không áp dụng mốc trước)'),
    'price_unparseable': ('Kiểu sai', 'price khác rỗng nhưng không đọc được thành số hữu hạn', 'Không thể tính median', 'Đặt price=None, gắn cờ'),
    'price_outlier': ('Ngoại lai', 'price <= 0 (price_nonpositive) hoặc price > qa.price_max (price_outlier_high)', 'Giá đêm không thể không dương; rào chắn lỗi nhập liệu cực lớn', 'Đặt price=None, giữ dòng, gắn cờ'),
    'room_type_unknown': ('Category drift', 'room_type khác rỗng nhưng không thuộc qa.room_types', 'Phát hiện danh mục mới/đổi tên giữa các mốc', 'Gắn cờ, giữ nguyên giá trị'),
    'coordinates_invalid': ('Địa lý', 'latitude/longitude rỗng, không phải số hữu hạn, ngoài [-90,90]/[-180,180] hoặc (0,0)', 'Không đặt được lên bản đồ', 'Đặt tọa độ=None, gắn cờ'),
    'coordinates_outside_city': ('Địa lý', 'Tọa độ hợp lệ nhưng ngoài hộp bao qa.bbox của thành phố', 'Nghi sai vị trí; không tự sửa', 'Gắn cờ (bỏ qua nếu config không có qa.bbox)'),
    'neighbourhood_missing': ('Thiếu', 'neighbourhood_cleansed rỗng', 'KPI neighbourhood cần cột gốc; không điền bằng analysis_area', 'Gắn cờ, không điền'),
    'neighbourhood_not_in_reference': ('Toàn vẹn tham chiếu', 'neighbourhood_cleansed khác rỗng nhưng không có trong neighbourhoods.geojson của mốc', 'Không nối được với ranh giới/bản đồ', 'Chỉ báo cáo số dòng (chạy sau clean_listings, không thêm cờ)'),
    'min_nights_outlier': ('Ngoại lai', 'minimum_nights > qa.min_nights_cap (mặc định 365)', 'Nghi giá trị nhập sai hoặc listing không cho thuê ngắn hạn', 'Gắn cờ'),
    'date_invalid': ('Ngày sai', 'last_scraped/host_since/first_review/last_review không phải ngày ISO (date_unparseable) hoặc first_review > last_review, last_review/host_since > last_scraped (date_order_invalid)', 'Ngày sai làm hỏng phân tích thời gian', 'Gắn cờ'),
    'scrape_date_offset': ('Ngày sai', '|last_scraped - snapshot_date| > qa.max_scrape_lag_days (mặc định 3 ngày)', 'Dòng được thu thập lệch xa ngày mốc, ảnh hưởng so sánh theo thời gian', 'Gắn cờ'),
    'cross_host_id_changed': ('Giữa các mốc', 'Cùng listing_id ở hai mốc liền kề nhưng host_id khác', 'Collision/đổi chủ; làm sai tỷ lệ host nhiều listing nếu bỏ qua', 'Chỉ báo cáo số cặp'),
    'cross_category_changed': ('Giữa các mốc', 'Cùng listing_id nhưng room_type hoặc neighbourhood_cleansed khác giữa hai mốc liền kề', 'Đổi loại phòng/khu vực làm lệch KPI theo thời gian', 'Chỉ báo cáo số cặp (chi tiết room_type/neighbourhood trong cột action)'),
    'cross_coordinates_moved': ('Giữa các mốc', 'Cùng listing_id, tọa độ dịch > qa.coord_shift_km (mặc định 1 km)', 'Nghi sai tọa độ hoặc gộp nhầm listing', 'Chỉ báo cáo số cặp'),
    'schema_drift': ('Schema', 'Tập cột listings của mốc khác mốc liền trước', 'Cột thêm/bớt làm hỏng parser hoặc KPI', 'Chỉ báo cáo cột thêm/bớt'),
}

# Processed schema (docs: data dictionary). Thứ tự = thứ tự cột pipeline xuất.
DICTIONARY = (
    ('snapshot_date', 'date', 'Ngày mốc (YYYY-MM-DD) theo config/workbook', 'config', 'Khóa cùng listing_id'),
    ('listing_id', 'str', 'ID listing, giữ nguyên chuỗi (nhiều ID > 2^53)', 'listings.id', 'id_missing, id_format, duplicate_key'),
    ('host_id', 'str', 'ID host, giữ nguyên chuỗi', 'listings.host_id', 'critical_field_missing, cross_host_id_changed'),
    ('price', 'float|None', 'Giá mỗi đêm, CAD; chỉ dùng ở mốc cuối; None nếu thiếu/lỗi', 'listings.price', 'price_missing_final, price_unparseable, price_outlier'),
    ('room_type', 'str', 'Loại phòng như trong nguồn (không chuẩn hóa)', 'listings.room_type', 'critical_field_missing, room_type_unknown'),
    ('analysis_area', 'str', 'Vùng chữ nhật A01–A08 của workbook; không phải neighbourhood hành chính', 'workbook sheet Listing', 'critical_field_missing'),
    ('neighbourhood_cleansed', 'str', 'Neighbourhood theo Inside Airbnb; không điền khi thiếu', 'listings.neighbourhood_cleansed', 'neighbourhood_missing, neighbourhood_not_in_reference'),
    ('latitude', 'float|None', 'Vĩ độ WGS84; None nếu không hợp lệ', 'listings.latitude', 'coordinates_invalid, coordinates_outside_city'),
    ('longitude', 'float|None', 'Kinh độ WGS84; None nếu không hợp lệ', 'listings.longitude', 'coordinates_invalid, coordinates_outside_city'),
    ('qa_flags', 'str', 'Tên các cờ QA nối bằng "|", sắp xếp; rỗng nếu không có', 'qa.py', 'tất cả rule gắn cờ'),
)


def rule_catalog():
    """Bảng Name → Condition → Reason → Action theo đề bài (một dòng mỗi rule)."""
    return [{'rule': name, 'group': g, 'condition': c, 'reason': r, 'action': a}
            for name, (g, c, r, a) in RULES.items()]


def data_dictionary():
    return [{'column': c, 'type': t, 'description': d, 'source': s, 'qa_rules': q}
            for c, t, d, s, q in DICTIONARY]


def _text(value):
    return (value or '').strip()


def parse_price(value):
    """'$1,250.00' -> 1250.0. Trả (giá, trạng thái): 'ok' | 'blank' | 'bad'."""
    text = _text(value)
    if not text:
        return None, 'blank'
    try:
        number = float(text.replace('$', '').replace(',', '').strip())
    except ValueError:
        return None, 'bad'
    return (number, 'ok') if isfinite(number) else (None, 'bad')


def parse_float(value):
    text = _text(value)
    if not text:
        return None, 'blank'
    try:
        number = float(text)
    except ValueError:
        return None, 'bad'
    return (number, 'ok') if isfinite(number) else (None, 'bad')


def parse_date(value):
    """'2026-06-15' -> date. Trả (date, trạng thái): 'ok' | 'blank' | 'bad'."""
    text = _text(value)
    if not text:
        return None, 'blank'
    try:
        return date.fromisoformat(text), 'ok'
    except ValueError:
        return None, 'bad'


def _is_plain_id(text):
    # ID Airbnb là số nguyên dương; "12.0", "1.2e+17" hay "abc" là dấu hiệu qua float/Excel.
    return text.isascii() and text.isdigit()


def _median_price(rows):
    prices = [row['price'] for row in rows if row['price'] is not None]
    return median(prices) if prices else None


def neighbourhood_names(geojson):
    """Tên neighbourhood từ nội dung neighbourhoods.geojson đã json.load (hàm thuần)."""
    return {_text(f.get('properties', {}).get('neighbourhood')) for f in geojson.get('features', [])} - {''}


def check_neighbourhood_reference(listings, names_by_snapshot):
    """Toàn vẹn tham chiếu: neighbourhood_cleansed phải có trong neighbourhoods.geojson của mốc.

    listings: bảng đã làm sạch của mọi mốc; names_by_snapshot: {snapshot: tập tên} (xem
    neighbourhood_names). Mốc không có trong dict bị bỏ qua. Trả QA rows, chỉ báo cáo.
    Giá trị rỗng không tính ở đây (đã có neighbourhood_missing). Hàm thuần.
    """
    by_snapshot = {}
    for row in listings:
        by_snapshot.setdefault(row['snapshot_date'], []).append(row)
    out = []
    for snapshot, names in names_by_snapshot.items():
        rows = by_snapshot.get(snapshot, [])
        bad = sum(bool(r['neighbourhood_cleansed']) and r['neighbourhood_cleansed'] not in names for r in rows)
        out.append({'snapshot_date': snapshot, 'rule': REFERENCE_RULE, 'affected_rows': bad,
                    'action': f'report_only [reference_names={len(names)}]', 'rows_after': len(rows),
                    'median_price_before': None, 'median_price_after': None})
    return out


def _parse_row(row, snapshot):
    price, price_status = parse_price(row.get('price'))
    lat, _ = parse_float(row.get('latitude'))
    lon, _ = parse_float(row.get('longitude'))
    return {
        'snapshot_date': snapshot,
        'listing_id': _text(row.get('id')),
        'host_id': _text(row.get('host_id')),
        'price': price,
        'room_type': _text(row.get('room_type')),
        'analysis_area': _text(row.get('analysis_area')),
        'neighbourhood_cleansed': _text(row.get('neighbourhood_cleansed')),
        'latitude': lat, 'longitude': lon,
        '_flags': set(), '_price_status': price_status,
        '_min_nights': parse_float(row.get('minimum_nights'))[0],
        '_dates': {c: parse_date(row.get(c)) for c in DATE_COLUMNS},
    }


def clean_listings(records, snapshot, cfg):
    """records: iterator raw listings đã lọc ID, có analysis_area (đọc đúng một lần).

    Trả (cleaned_rows, qa_report_rows), không sửa raw.
    cleaned: snapshot_date, listing_id/host_id dạng str, price float/None, room_type,
    analysis_area, neighbourhood_cleansed, latitude, longitude, qa_flags (nối '|').
    QA report: snapshot_date, rule, affected_rows, action, rows_after,
    median_price_before, median_price_after. Rule chạy tuần tự nên rows_after và median
    là trạng thái tích lũy sau khi áp rule đó.
    """
    qa_cfg = {**DEFAULTS, **cfg.get('qa', {})}
    room_types = set(qa_cfg.get('room_types', ()))
    bbox = qa_cfg.get('bbox')
    is_final = snapshot == cfg.get('price_snapshot', cfg['snapshots'][-1])
    snapshot_day = date.fromisoformat(snapshot)

    raw = list(records)
    columns = set().union(*raw) if raw else set()
    missing_columns = sorted(set(REQUIRED_COLUMNS) - columns) if raw else []

    rows = [_parse_row(row, snapshot) for row in raw]
    report = []

    def log(rule, affected, action, median_before, extra=''):
        report.append({
            'snapshot_date': snapshot, 'rule': rule, 'affected_rows': affected,
            'action': action + (f' [{extra}]' if extra else ''),
            'rows_after': len(rows),
            'median_price_before': median_before,
            'median_price_after': _median_price(rows),
        })

    def apply(rule, checks, action='flag', mutate=None):
        """Mỗi check = (tên cờ, predicate). affected_rows = số dòng dính ít nhất một check."""
        before = _median_price(rows)  # trước khi mutate sửa giá/tọa độ tại chỗ
        per_flag, hit = dict.fromkeys((name for name, _ in checks), 0), 0
        for row in rows:
            hits = [name for name, predicate in checks if predicate(row)]
            for name in hits:
                row['_flags'].add(name)
                per_flag[name] += 1
            if hits:
                hit += 1
                if mutate:
                    mutate(row)
        log(rule, hit, action, before, ','.join(f'{k}={v}' for k, v in per_flag.items()) if len(checks) > 1 else '')

    def skip(rule, why):
        log(rule, 0, f'skip_{why}', _median_price(rows))

    log('raw_input', len(rows), 'none', _median_price(rows),
        'missing_columns=' + ','.join(missing_columns) if missing_columns else '')

    # 1) Khóa: thiếu ID -> drop; ID sai dạng -> flag.
    before = _median_price(rows)
    kept = [row for row in rows if row['listing_id']]
    dropped = len(rows) - len(kept)
    rows[:] = kept
    log('id_missing', dropped, 'drop', before)
    apply('id_format', [('id_format', lambda r: not _is_plain_id(r['listing_id']))])

    # 2) Trùng khóa trong mốc: giữ dòng đầu, drop dòng sau; đếm cả trường hợp nội dung khác nhau.
    before = _median_price(rows)
    first_seen, unique, conflicts = {}, [], 0
    for row in rows:
        first = first_seen.get(row['listing_id'])
        if first is None:
            first_seen[row['listing_id']] = row
            unique.append(row)
        else:
            first['_flags'].add('duplicate_key')
            conflicts += any(first[f] != row[f] for f in ('host_id', 'price', 'room_type', 'latitude', 'longitude'))
    dup = len(rows) - len(unique)
    rows[:] = unique
    log('duplicate_key', dup, 'drop_later_keep_first', before, f'conflicting={conflicts}' if dup else '')

    # 3) Thiếu / kiểu sai / ngoại lai.
    apply('critical_field_missing', [('host_id_missing', lambda r: not r['host_id']),
                                     ('room_type_missing', lambda r: not r['room_type']),
                                     ('analysis_area_missing', lambda r: not r['analysis_area'])])
    if is_final:
        apply('price_missing_final', [('price_missing_final', lambda r: r['_price_status'] == 'blank')])
    else:
        skip('price_missing_final', 'not_final_snapshot')
    apply('price_unparseable', [('price_unparseable', lambda r: r['_price_status'] == 'bad')])
    apply('price_outlier', [('price_nonpositive', lambda r: r['price'] is not None and r['price'] <= 0),
                            ('price_outlier_high', lambda r: r['price'] is not None and r['price'] > qa_cfg['price_max'])],
          action='null_price', mutate=lambda r: r.update(price=None))

    # 4) Danh mục (category drift).
    apply('room_type_unknown', [('room_type_unknown',
                                 lambda r: bool(r['room_type']) and bool(room_types) and r['room_type'] not in room_types)])

    # 5) Tọa độ: lỗi -> None; ngoài hộp bao thành phố -> chỉ cờ.
    def bad_coord(r):
        lat, lon = r['latitude'], r['longitude']
        return (lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180
                or (lat == 0 and lon == 0))

    apply('coordinates_invalid', [('coordinates_invalid', bad_coord)], action='null_coordinates',
          mutate=lambda r: r.update(latitude=None, longitude=None))
    if bbox:
        apply('coordinates_outside_city', [('coordinates_outside_city', lambda r: r['latitude'] is not None and not (
            bbox['lat_min'] <= r['latitude'] <= bbox['lat_max'] and bbox['lon_min'] <= r['longitude'] <= bbox['lon_max']))])
    else:
        skip('coordinates_outside_city', 'no_bbox_in_config')

    # 6) Neighbourhood thiếu: không điền bằng analysis_area.
    apply('neighbourhood_missing', [('neighbourhood_missing', lambda r: not r['neighbourhood_cleansed'])])

    # 7) minimum_nights và ngày.
    apply('min_nights_outlier', [('min_nights_outlier',
                                  lambda r: r['_min_nights'] is not None and r['_min_nights'] > qa_cfg['min_nights_cap'])])

    def d(row, column):
        return row['_dates'][column][0]

    def order_invalid(r):
        first, last, scraped, since = d(r, 'first_review'), d(r, 'last_review'), d(r, 'last_scraped'), d(r, 'host_since')
        return bool((first and last and first > last) or (last and scraped and last > scraped)
                    or (since and scraped and since > scraped))

    apply('date_invalid', [('date_unparseable', lambda r: any(s == 'bad' for _, s in r['_dates'].values())),
                           ('date_order_invalid', order_invalid)])
    apply('scrape_date_offset', [('scrape_date_offset', lambda r: d(r, 'last_scraped') is not None and abs(
        (d(r, 'last_scraped') - snapshot_day).days) > qa_cfg['max_scrape_lag_days'])])

    cleaned = []
    for row in rows:
        out = {k: v for k, v in row.items() if not k.startswith('_')}
        out['qa_flags'] = '|'.join(sorted(row['_flags']))
        cleaned.append(out)
    return cleaned, report


def compare_schemas(columns_by_snapshot):
    """Schema drift giữa các mốc. columns_by_snapshot: {snapshot: iterable tên cột}, theo thứ tự mốc.

    Trả QA rows (rule schema_drift, affected_rows = số cột thêm + bỏ so với mốc liền trước).
    Hàm thuần: nhóm trưởng gọi nếu cần ghi vào qa_report; không đụng dữ liệu.
    """
    out, previous = [], None
    for snapshot, columns in columns_by_snapshot.items():
        current = set(columns)
        if previous is not None:
            added, dropped = sorted(current - previous), sorted(previous - current)
            out.append({
                'snapshot_date': snapshot, 'rule': SCHEMA_RULE,
                'affected_rows': len(added) + len(dropped),
                'action': f"flag [added={','.join(added)}; dropped={','.join(dropped)}]",
                'rows_after': None, 'median_price_before': None, 'median_price_after': None,
            })
        previous = current
    return out


def _km(lat1, lon1, lat2, lon2):
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(a))


def cross_snapshot_checks(listings, cfg):
    """Kiểm collision giữa các mốc liền kề trên bảng listings đã làm sạch (mọi mốc).

    Trả QA rows cho từng mốc từ mốc thứ hai: affected_rows là số listing có mặt ở cả hai mốc
    mà thuộc tính đổi. Chỉ báo cáo, không sửa. Cùng listing xuất hiện ở nhiều mốc KHÔNG phải
    duplicate (khóa là snapshot_date + listing_id). Hàm thuần; nhóm trưởng gọi trong pipeline.
    """
    shift_km = {**DEFAULTS, **cfg.get('qa', {})}['coord_shift_km']
    by_snapshot = {}
    for row in listings:
        by_snapshot.setdefault(row['snapshot_date'], {})[row['listing_id']] = row
    order = [s for s in cfg['snapshots'] if s in by_snapshot]
    out = []
    for previous, current in zip(order, order[1:]):
        before, after = by_snapshot[previous], by_snapshot[current]
        both = before.keys() & after.keys()
        host = category = moved = room = area = 0
        for key in both:
            a, b = before[key], after[key]
            host += a['host_id'] != b['host_id']
            room_changed = a['room_type'] != b['room_type']
            area_changed = a['neighbourhood_cleansed'] != b['neighbourhood_cleansed']
            room += room_changed
            area += area_changed
            category += room_changed or area_changed
            if None not in (a['latitude'], a['longitude'], b['latitude'], b['longitude']):
                moved += _km(a['latitude'], a['longitude'], b['latitude'], b['longitude']) > shift_km
        for rule, count, extra in (('cross_host_id_changed', host, ''),
                                   ('cross_category_changed', category, f'room_type={room},neighbourhood={area}; '),
                                   ('cross_coordinates_moved', moved, '')):
            out.append({'snapshot_date': current, 'rule': rule, 'affected_rows': count,
                        'action': f'report_only [{extra}vs {previous}; compared={len(both)}]',
                        'rows_after': len(after), 'median_price_before': None, 'median_price_after': None})
    return out


def missing_rates(raw_rows, snapshot, columns=None):
    """Mức độ thiếu của cột chính trên raw: phân biệt thiếu CỘT (present=False) với giá trị trống."""
    rows = list(raw_rows)
    present = set().union(*rows) if rows else set()
    out = []
    for column in columns or PROFILE_COLUMNS:
        has = column in present
        empty = sum(not _text(row.get(column)) for row in rows) if has else len(rows)
        out.append({'snapshot_date': snapshot, 'column': column, 'column_present': has, 'rows': len(rows),
                    'missing': empty, 'missing_rate': round(empty / len(rows), 4) if rows else None})
    return out


def _market(rows):
    """KPI nền (công thức theo docs/KPI.md) trên các dòng đã parse/cleaned, cùng một mốc."""
    prices = [r['price'] for r in rows if r['price'] is not None]
    typed = [r for r in rows if r['room_type']]
    hosts = [r['host_id'] for r in rows if r['host_id']]
    per_host = Counter(hosts)
    return {
        'supply': len(rows),
        'price_n': len(prices),
        'median_price': median(prices) if prices else None,
        'entire_home_share': (sum(r['room_type'] == 'Entire home/apt' for r in typed) / len(typed)) if typed else None,
        'multi_listing_host_share': (sum(per_host[h] > 1 for h in hosts) / len(hosts)) if hosts else None,
    }


def kpi_impact(raw_rows, cleaned_rows, snapshot):
    """Ảnh hưởng QA lên KPI nền: giá trị trước (raw đã parse) và sau (cleaned) của mốc.

    Công thức là bản tối thiểu để đo tác động QA; KPI chính thức do kpi.summarize (TV3) tính.
    """
    before = _market([_parse_row(row, snapshot) for row in raw_rows])
    after = _market(cleaned_rows)
    out = []
    for kpi, b in before.items():
        a = after[kpi]
        out.append({'snapshot_date': snapshot, 'kpi': kpi, 'before': b, 'after': a,
                    'delta': None if b is None or a is None else a - b})
    return out


def run_listings_qa(raw_by_snapshot, cfg, names_by_snapshot=None):
    """Chạy toàn bộ QA listings cho mọi mốc: gom các hàm ở trên theo đúng thứ tự.

    raw_by_snapshot: {snapshot: iterable raw rows đã lọc ID, có analysis_area}.
    names_by_snapshot: {snapshot: tập tên neighbourhood} (tùy chọn) cho kiểm tham chiếu.
    Trả dict: cleaned, qa_report, kpi_impact, missingness. Hàm thuần, không đọc/ghi file.
    """
    profile_columns = cfg.get('qa', {}).get('profile_columns')
    cleaned, report, impact, missing, columns = [], [], [], [], {}
    for snapshot in cfg['snapshots']:
        if snapshot not in raw_by_snapshot:
            continue
        raw = list(raw_by_snapshot[snapshot])
        columns[snapshot] = (set().union(*raw) if raw else set()) - {'analysis_area'}  # cột do loader thêm
        rows, rule_rows = clean_listings(iter(raw), snapshot, cfg)
        cleaned.extend(rows)
        report.extend(rule_rows)
        impact.extend(kpi_impact(raw, rows, snapshot))
        missing.extend(missing_rates(raw, snapshot, profile_columns or sorted(columns[snapshot])))
    report.extend(compare_schemas(columns))
    report.extend(cross_snapshot_checks(cleaned, cfg))
    if names_by_snapshot:
        report.extend(check_neighbourhood_reference(cleaned, names_by_snapshot))
    return {'cleaned': cleaned, 'qa_report': report, 'kpi_impact': impact, 'missingness': missing}
