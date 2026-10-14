"""Assigned-data checks before cleaning; separate outputs for each team member."""
from collections import Counter
import csv
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
from .assignment import identifier, load_assignment
from .io import write_csv

PARTS = ('listings', 'listing-details', 'calendar', 'reviews')
FILES = {'listings': 'listings_summary.csv', 'listing-details': 'listing_details.csv',
         'calendar': 'calendar_summary.csv', 'reviews': 'reviews_summary.csv'}
FINAL_FIELDS = ['ma_du_lieu', 'moc', 'ngay', 'tai_ve_ok', 'listings_bytes',
                'calendar_bytes', 'reviews_bytes', 'listings_dong', 'calendar_dong',
                'reviews_dong', 'entire_home', 'private_room', 'khong_co_review',
                'thieu_price', 'so_cot_listings', 'so_cot_nan_90']
COMMON = ['ma_du_lieu', 'moc', 'ngay', 'status', 'error', 'assignment_sha256', 'source_sha256']
METRICS = {
    'listings': ['listings_bytes', 'listings_dong', 'so_cot_listings', 'so_cot_nan_90', 'listing_count', 'missing_ids_count', 'duplicate_ids'],
    'listing-details': ['listings_bytes', 'listings_dong', 'entire_home', 'private_room', 'khong_co_review', 'thieu_price'],
    'calendar': ['calendar_bytes', 'calendar_dong', 'listing_count', 'missing_ids_count', 'duplicate_keys', 'invalid_date_rows', 'invalid_available_rows', 'not365_listing_count'],
    'reviews': ['reviews_bytes', 'reviews_dong', 'review_count', 'missing_ids_count', 'duplicate_ids'],
}


def context(config_path, assignment_path=None):
    config_path = Path(config_path).resolve()
    root = config_path.parent.parent
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    path = Path(assignment_path).expanduser().resolve() if assignment_path else root / cfg['assignment']
    assignment = load_assignment(path, cfg['course_class'], cfg['group'])
    if assignment.code != cfg['data_code']:
        raise ValueError('Workbook data code does not match configs/data_check.json')
    expected = cfg['expected']
    actual = {'listings': len(assignment.listing_ids), 'reviews': len(assignment.review_ids),
              'llm': len(assignment.llm_ids), 'manual': len(assignment.manual_ids)}
    if any(actual[k] != expected[k] for k in actual):
        raise ValueError(f'Workbook assignment counts differ from config: {actual}')
    return root, cfg, assignment


def file_digest(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def missing(value):
    return value.strip().lower() in {'', 'nan'}


def selected_rows(path, required, key, assigned):
    """Yield columns and a stream of matching raw rows; no dedupe, no removal of missing data."""
    csv.field_size_limit(16 * 1024 * 1024)
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        fields = next(reader, [])
        if len(fields) != len(set(fields)) or set(required) - set(fields):
            raise ValueError(f'Missing required or duplicate columns: {sorted(set(required)-set(fields))}')
        index = fields.index(key)
        yield fields
        for row in reader:
            if not row:  # CSV blank lines are not records.
                continue
            if len(row) != len(fields):
                raise ValueError(f'Malformed CSV record at physical line {reader.line_num}')
            # IDs in the raw file must be integers represented as strings.
            value = row[index].strip()
            if value in assigned:
                yield row


def listings_check(path, assignment, expected, position, details=False):
    iterator = selected_rows(path, ['id', 'room_type', 'number_of_reviews', 'price'], 'id', assignment.listing_ids)
    fields = next(iterator)
    indexes = {name: fields.index(name) for name in ['id', 'room_type', 'number_of_reviews', 'price']}
    counts, nulls, ids = Counter(), Counter(), Counter()
    for row in iterator:
        counts['rows'] += 1
        ids[row[indexes['id']].strip()] += 1
        for field, value in zip(fields, row):
            nulls[field] += missing(value)
        room = row[indexes['room_type']]
        counts['entire_home'] += room == 'Entire home/apt'
        counts['private_room'] += room == 'Private room'
        counts['khong_co_review'] += row[indexes['number_of_reviews']].strip() in {'0', '0.0'}
        counts['thieu_price'] += missing(row[indexes['price']])
    absent = sorted(assignment.listing_ids - ids.keys())
    duplicates = sum(n-1 for n in ids.values())
    n = counts['rows']
    high = [{'column': f, 'missing_count': nulls[f], 'rows': n, 'missing_rate': nulls[f]/n}
            for f in fields if n and nulls[f]/n >= 0.9]
    errors = []
    if n != expected['listings'] or absent or duplicates:
        errors.append(f'Expected {expected["listings"]} unique listings; rows={n}, missing IDs={len(absent)}, duplicates={duplicates}')
    metrics = {'listings_dong': n, 'so_cot_listings': len(fields), 'so_cot_nan_90': len(high) if n else '',
               'listing_count': len(ids), 'missing_ids_count': len(absent), 'duplicate_ids': duplicates,
               **{k: counts[k] for k in ['entire_home', 'private_room', 'khong_co_review', 'thieu_price']}}
    if details:
        for field, key in [('entire_home', 'entire_home'), ('private_room', 'private_room')]:
            if metrics[field] != expected[key]:
                errors.append(f'{field}: expected {expected[key]}, observed {metrics[field]}')
        wanted = expected['no_reviews'][position-1]
        if metrics['khong_co_review'] != wanted:
            errors.append(f'khong_co_review: expected {wanted}, observed {metrics["khong_co_review"]}')
        if position == 4 and metrics['thieu_price'] != expected['missing_price_last']:
            errors.append(f'Last snapshot missing price: expected {expected["missing_price_last"]}, observed {metrics["thieu_price"]}')
    return metrics, errors, {'missing_ids': absent, 'high_missing_columns': high}


def calendar_check(path, assignment, expected):
    iterator = selected_rows(path, ['listing_id', 'date', 'available'], 'listing_id', assignment.listing_ids)
    fields = next(iterator)
    lid, day, available = [fields.index(f) for f in ['listing_id', 'date', 'available']]
    ids, seen = Counter(), set()
    n = duplicates = bad_dates = bad_available = 0
    for row in iterator:
        n += 1
        key = row[lid].strip()
        ids[key] += 1
        pair = (key, row[day])
        duplicates += pair in seen
        seen.add(pair)
        try:
            if date.fromisoformat(row[day]).isoformat() != row[day]:
                bad_dates += 1
        except ValueError:
            bad_dates += 1
        bad_available += row[available].strip().lower() not in {'t', 'f'}
    absent = sorted(assignment.listing_ids - ids.keys())
    days = expected['calendar_days_per_listing']
    wrong = sum(count != days for count in ids.values())
    wanted = expected['listings'] * days
    errors = []
    if n != wanted or absent or wrong:
        errors.append(f'Expected {wanted} rows, {expected["listings"]} listings and {days} days/listing; observed {n} rows, missing IDs={len(absent)}, wrong day counts={wrong}')
    if duplicates or bad_dates or bad_available:
        errors.append(f'duplicate keys={duplicates}, invalid dates={bad_dates}, invalid available={bad_available}')
    return {'calendar_dong': n, 'listing_count': len(ids), 'missing_ids_count': len(absent),
            'duplicate_keys': duplicates, 'invalid_date_rows': bad_dates,
            'invalid_available_rows': bad_available, 'not365_listing_count': wrong}, errors, {'missing_ids': absent}


def reviews_check(path, assignment, expected):
    iterator = selected_rows(path, ['id', 'listing_id', 'date', 'comments'], 'id', assignment.review_ids)
    fields = next(iterator)
    index = fields.index('id')
    ids = Counter(row[index].strip() for row in iterator)
    n = sum(ids.values())
    absent = sorted(assignment.review_ids - ids.keys())
    duplicates = sum(value-1 for value in ids.values())
    errors = []
    if n != expected['reviews'] or absent or duplicates:
        errors.append(f'Expected {expected["reviews"]} reviews; observed {n}, missing IDs={len(absent)}, duplicates={duplicates}')
    return {'reviews_dong': n, 'review_count': len(ids), 'missing_ids_count': len(absent), 'duplicate_ids': duplicates}, errors, {'missing_ids': absent}


def run_part(root, cfg, assignment, part):
    output = root / cfg['output']
    output.mkdir(parents=True, exist_ok=True)
    filename = 'calendar.csv.gz' if part == 'calendar' else 'reviews.csv.gz' if part == 'reviews' else 'listings.csv.gz'
    byte_key = 'calendar_bytes' if part == 'calendar' else 'reviews_bytes' if part == 'reviews' else 'listings_bytes'
    rows, diagnostics, missing_columns = [], [], []
    for i, snapshot in enumerate(assignment.snapshots, start=1):
        path = root / cfg['raw'] / snapshot / filename
        result = {key: '' for key in COMMON + METRICS[part]}
        result.update(ma_du_lieu=assignment.code, moc=i, ngay=snapshot, assignment_sha256=assignment.fingerprint)
        detail = {'ma_du_lieu': assignment.code, 'moc': i, 'ngay': snapshot, 'part': part}
        try:
            result[byte_key] = path.stat().st_size
            result['source_sha256'] = file_digest(path)
            if part in {'listings', 'listing-details'}:
                metrics, errors, info = listings_check(path, assignment, cfg['expected'], i, part == 'listing-details')
            elif part == 'calendar':
                metrics, errors, info = calendar_check(path, assignment, cfg['expected'])
            else:
                metrics, errors, info = reviews_check(path, assignment, cfg['expected'])
            result.update({key: metrics[key] for key in METRICS[part] if key in metrics})
            result['status'] = 'count_or_quality_mismatch' if errors else 'ok'
            result['error'] = '; '.join(errors)
            detail.update(info)
            if part == 'listings':
                missing_columns.extend({'ma_du_lieu': assignment.code, 'moc': i, 'ngay': snapshot, 'assignment_sha256': assignment.fingerprint, 'source_sha256': result['source_sha256'], **r} for r in info['high_missing_columns'])
        except FileNotFoundError:
            result.update(status='missing_file', error=f'Missing local file: {path.relative_to(root)}')
        except (OSError, EOFError, ValueError, csv.Error) as exc:
            result.update(status='read_error', error=str(exc))
        detail.update(status=result['status'], error=result['error'])
        diagnostics.append(detail)
        rows.append(result)
        print(f'{part} {snapshot}: {result["status"]}', flush=True)
    write_csv(output / FILES[part], rows, COMMON + METRICS[part])
    if part == 'listings':
        write_csv(output / 'missing_columns.csv', missing_columns,
                  ['ma_du_lieu', 'moc', 'ngay', 'assignment_sha256', 'source_sha256', 'column', 'missing_count', 'rows', 'missing_rate'])
    if part == 'reviews':
        write_csv(output / 'review_sample_counts.csv', [{'ma_du_lieu': assignment.code,
                  'assignment_sha256': assignment.fingerprint, 'source': 'workbook Review: x markers',
                  'mau_llm': len(assignment.llm_ids), 'nhan_tay': len(assignment.manual_ids)}])
    (output / f'{part}_diagnostics.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    notes = [f'# {part} — kết quả kiểm tra dữ liệu', '',
             f'Mã dữ liệu: {assignment.code}. Ngày lấy từ workbook. Thống kê trước cleaning.', '',
             '## Trạng thái từng mốc', '']
    notes.extend(f'- {r["ngay"]}: {r["status"]}. {r["error"]}'.rstrip() for r in rows)
    if part == 'listing-details':
        notes += ['', '## Câu 4', '', 'Chỉ phân tích giá listings ở mốc cuối. Giá rỗng ở các mốc trước không phải lý do xin cấp lại. Calendar không dùng cho phân tích giá.']
    if part == 'reviews':
        notes += ['', '## Câu 2', '', f'Mẫu LLM: {len(assignment.llm_ids)}. Nhãn tay: {len(assignment.manual_ids)}. Đếm trực tiếp dấu x trong hai cột workbook, không lấy từ pipeline hoặc API.']
    (output / f'{part}_notes.md').write_text('\n'.join(notes) + '\n', encoding='utf-8')
    print(f'Saved: {output / FILES[part]}', flush=True)
    return all(row['status'] == 'ok' for row in rows)


def read_part(output, name, assignment, expected):
    with (output / FILES[name]).open(encoding='utf-8', newline='') as stream:
        records = list(csv.DictReader(stream))
    if not records or set(COMMON + METRICS[name]) - set(records[0]):
        raise ValueError(f'{FILES[name]} is missing required columns')
    if len(records) != 4:
        raise ValueError(f'{FILES[name]} must have exactly four rows')
    indexes = {}
    for row in records:
        if row['ma_du_lieu'] != assignment.code or row['assignment_sha256'] != assignment.fingerprint:
            raise ValueError(f'{FILES[name]} has another group or workbook version')
        snapshot = row['ngay']
        if snapshot not in assignment.snapshots or snapshot in indexes:
            raise ValueError(f'{FILES[name]} has wrong or duplicate snapshot')
        if row['moc'] != str(assignment.snapshots.index(snapshot)+1):
            raise ValueError(f'{FILES[name]} has wrong snapshot order')
        if row['status'] not in {'ok', 'count_or_quality_mismatch', 'missing_file', 'read_error'}:
            raise ValueError(f'{FILES[name]} has an unknown status')
        if row['status'] == 'ok':
            for metric in METRICS[name]:
                if not row[metric].isdigit():
                    raise ValueError(f'{FILES[name]}: {metric} must be a nonnegative integer')
            if name in {'listings', 'listing-details'} and int(row['listings_dong']) != expected['listings']:
                raise ValueError(f'{FILES[name]}: listings row count does not match assignment')
            if name == 'calendar' and (int(row['calendar_dong']) != expected['listings']*expected['calendar_days_per_listing'] or int(row['listing_count']) != expected['listings']):
                raise ValueError(f'{FILES[name]}: calendar counts do not match assignment')
            if name == 'reviews' and (int(row['reviews_dong']) != expected['reviews'] or int(row['review_count']) != expected['reviews']):
                raise ValueError(f'{FILES[name]}: review counts do not match assignment')
            if name == 'listing-details':
                wanted = {'entire_home': expected['entire_home'], 'private_room': expected['private_room'],
                          'khong_co_review': expected['no_reviews'][assignment.snapshots.index(snapshot)]}
                if snapshot == assignment.snapshots[-1]:
                    wanted['thieu_price'] = expected['missing_price_last']
                if any(int(row[k]) != v for k,v in wanted.items()):
                    raise ValueError(f'{FILES[name]}: listing controls do not match assignment')
            for key in ['missing_ids_count', 'duplicate_ids', 'duplicate_keys', 'invalid_date_rows', 'invalid_available_rows', 'not365_listing_count']:
                if key in row and int(row[key]) != 0:
                    raise ValueError(f'{FILES[name]}: status ok conflicts with {key}')
        indexes[snapshot] = row
    return indexes


def merge(root, cfg, assignment):
    output = root / cfg['output']
    output.mkdir(parents=True, exist_ok=True)
    tables, blockers = {}, []
    for part in PARTS:
        try:
            tables[part] = read_part(output, part, assignment, cfg['expected'])
        except (OSError, ValueError, KeyError) as exc:
            blockers.append(f'{part}: {exc}')
    final = []
    for i, snapshot in enumerate(assignment.snapshots, start=1):
        row = {field: '' for field in FINAL_FIELDS}
        row.update(ma_du_lieu=assignment.code, moc=i, ngay=snapshot)
        for part, table in tables.items():
            source = table[snapshot]
            if source['status'] != 'ok':
                blockers.append(f'{snapshot} {part}: {source["status"]} {source["error"]}')
            for field in FINAL_FIELDS[4:]:
                if field in source:
                    if row[field] != '' and row[field] != source[field]:
                        blockers.append(f'{snapshot}: conflicting {field} between outputs')
                    row[field] = source[field]
        a = tables.get('listings', {}).get(snapshot, {})
        b = tables.get('listing-details', {}).get(snapshot, {})
        if a and b and a['source_sha256'] != b['source_sha256']:
            blockers.append(f'{snapshot}: Đức and Hiếu used different listings files')
        if len(tables) == 4 and all(tables[p][snapshot]['status'] == 'ok' for p in PARTS):
            row['tai_ve_ok'] = 'co'
        else:
            row['tai_ve_ok'] = 'can_kiem_tra'
        final.append(row)
    # Reject stale outputs if raw data have changed since the members ran their checks.
    for snapshot in assignment.snapshots:
        for part, filename in [('listings', 'listings.csv.gz'), ('calendar', 'calendar.csv.gz'), ('reviews', 'reviews.csv.gz')]:
            source = tables.get(part, {}).get(snapshot)
            if not source or source['status'] != 'ok':
                continue
            path = root / cfg['raw'] / snapshot / filename
            if not path.exists() or file_digest(path) != source['source_sha256']:
                blockers.append(f'{snapshot} {part}: raw file changed or missing; rerun this part')
    try:
        with (output / 'missing_columns.csv').open(encoding='utf-8', newline='') as stream:
            column_rows = list(csv.DictReader(stream))
        seen_columns = set()
        column_counts = Counter()
        for item in column_rows:
            pair = (item['ngay'], item['column'])
            if item['ma_du_lieu'] != assignment.code or item['ngay'] not in assignment.snapshots or pair in seen_columns:
                raise ValueError('wrong group/snapshot or duplicate column')
            listing_row = tables.get('listings', {}).get(item['ngay'])
            if not listing_row or item['assignment_sha256'] != assignment.fingerprint or item['source_sha256'] != listing_row['source_sha256']:
                raise ValueError('column report came from another workbook or listings file')
            if not item['rows'].isdigit() or not item['missing_count'].isdigit():
                raise ValueError('invalid missing counts')
            count, total = int(item['missing_count']), int(item['rows'])
            if total != int(listing_row['listings_dong']) or not total or not 0.9 <= count/total <= 1:
                raise ValueError('invalid missing-column ratio')
            seen_columns.add(pair)
            column_counts[item['ngay']] += 1
        for snapshot in assignment.snapshots:
            row = tables.get('listings', {}).get(snapshot)
            if row and row['status'] == 'ok' and column_counts[snapshot] != int(row['so_cot_nan_90']):
                raise ValueError(f'{snapshot}: missing column count differs from listings summary')
    except (OSError, ValueError, KeyError) as exc:
        blockers.append(f'missing_columns.csv: {exc}')
    ready = not blockers
    final_path = output / f'check_{assignment.code}.csv'
    draft_path = output / f'check_{assignment.code}.draft.csv'
    if ready:
        write_csv(final_path, final, FINAL_FIELDS)
        draft_path.unlink(missing_ok=True)
    else:
        write_csv(draft_path, final, FINAL_FIELDS)
        # Remove only the generated final report in our managed output folder: a stale final must not look current.
        final_path.unlink(missing_ok=True)
    write_answers(output, assignment, tables, blockers, ready)
    (output / 'merge_status.json').write_text(json.dumps({'ready_to_submit': ready, 'blockers': blockers,
        'assignment_sha256': assignment.fingerprint, 'data_code': assignment.code, 'answers_need_human_review': True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Saved {"final" if ready else "DRAFT — NOT READY"}: {final_path if ready else draft_path}', flush=True)
    return ready


def write_answers(output, assignment, tables, blockers, ready):
    lines = ['# Câu trả lời báo cáo kiểm tra dữ liệu', '', f'Mã dữ liệu: {assignment.code}', '',
             '## 1. Có tệp nào không tải hoặc đọc được không?', '']
    issues = []
    for part in ['listings', 'calendar', 'reviews']:
        for snapshot, row in tables.get(part, {}).items():
            if row['status'] in {'missing_file', 'read_error'}:
                issues.append(f'{snapshot}, {part}: {row["error"]}')
    lines += issues or (['Đã đọc thành công đủ 12 file gốc đang lưu tại máy; không ghi nhận lỗi đọc.'] if ready else ['Chưa đủ kết quả để xác nhận cả 12 file. Xem merge_status.json.'])
    lines += ['', '## 2. Mẫu LLM và nhãn tay', '',
              f'Mẫu LLM: {len(assignment.llm_ids)} review. Nhãn tay: {len(assignment.manual_ids)} review. Lấy trực tiếp dấu x ở hai cột trong sheet Review của workbook; không lấy từ pipeline nhóm.', '',
              '## 3. Các cột listings có từ 90% giá trị thiếu trở lên', '']
    grouped = {s: [] for s in assignment.snapshots}
    try:
        with (output / 'missing_columns.csv').open(encoding='utf-8', newline='') as stream:
            for row in csv.DictReader(stream):
                if row['ma_du_lieu'] != assignment.code or row['ngay'] not in grouped:
                    raise ValueError('Invalid missing_columns.csv group/snapshot')
                grouped[row['ngay']].append(row['column'])
        for snapshot, columns in grouped.items():
            valid = tables.get('listings', {}).get(snapshot, {}).get('status') == 'ok'
            lines.append(f'- {snapshot}: ' + (', '.join(columns) if valid and columns else 'Không có cột thiếu ≥90%.' if valid else 'Chưa xác minh; chạy lại listings.'))
    except (OSError, KeyError, ValueError):
        lines.append('Chưa có danh sách cột hợp lệ; chạy lại listings.')
    lines += ['', '## 4. Cột dự định dùng nhưng bị rỗng', '',
              f'Chỉ sử dụng giá listings ở mốc cuối {assignment.snapshots[-1]}; không phân tích biến động giá qua bốn mốc. Giá rỗng ở các mốc trước không phải lý do xin cấp lại. Calendar chỉ dùng cho lịch và availability, không phân tích giá.',
              'Nhóm cần bổ sung quyết định đối với các cột khác dự định dùng sau khi xem danh sách ở câu 3.', '',
              '## 5. Kết luận', '']
    if ready:
        lines.append('Các file đọc được và số lượng kiểm soát khớp hướng dẫn. Dữ liệu đủ cho các bước kiểm tra được triển khai; nhóm trưởng cần xem lại câu 3–4 và xác nhận phạm vi phân tích trước khi nộp. Không xin cấp lại chỉ vì thiếu giá ở mốc trước.')
    else:
        lines += ['Chưa đủ căn cứ kết luận hoặc nộp báo cáo. Kiểm tra các vấn đề sau; không sửa số đếm để khớp kỳ vọng:'] + [f'- {item}' for item in blockers]
    (output / 'report_answers.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
