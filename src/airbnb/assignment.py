"""Read the lecturer's XLSX without Excel, third-party dependencies or file edits."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def identifier(value):
    """Preserve integer IDs exactly; never pass 18-digit IDs through float."""
    text = str(value).strip()
    if re.fullmatch(r'[0-9]+', text):
        return str(int(text))
    # Numeric XLSX cells may use decimal/scientific notation.
    try:
        number = Decimal(text)
        if number.is_finite() and number >= 0 and number == number.to_integral_value():
            return str(int(number))
    except InvalidOperation:
        pass
    raise ValueError(f'Invalid integer identifier: {text!r}')


class XlsxReader:
    def __init__(self, path):
        self.archive = ZipFile(path)
        self.strings = []
        try:
            if 'xl/sharedStrings.xml' in self.archive.namelist():
                with self.archive.open('xl/sharedStrings.xml') as stream:
                    for _, element in ET.iterparse(stream, events=('end',)):
                        if element.tag == NS + 'si':
                            self.strings.append(''.join(t.text or '' for t in element.iter(NS + 't')))
                            element.clear()
            rels = ET.fromstring(self.archive.read('xl/_rels/workbook.xml.rels'))
            targets = {r.attrib['Id']: r.attrib['Target'] for r in rels}
            workbook = ET.fromstring(self.archive.read('xl/workbook.xml'))
            self.sheets = {}
            for sheet in workbook.find(NS + 'sheets'):
                target = targets[sheet.attrib[REL + 'id']]
                target = target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/' + target)
                self.sheets[sheet.attrib['name']] = target
        except Exception:
            self.archive.close()
            raise

    def close(self):
        self.archive.close()

    def records(self, sheet):
        """Yield header-keyed rows; sparse/blank XLSX cells stay blank."""
        if sheet not in self.sheets:
            raise ValueError(f'Workbook missing sheet {sheet!r}')
        headers = None
        with self.archive.open(self.sheets[sheet]) as stream:
            for _, element in ET.iterparse(stream, events=('end',)):
                if element.tag != NS + 'row':
                    continue
                values = {}
                for cell in element.findall(NS + 'c'):
                    col = re.match(r'[A-Z]+', cell.attrib['r']).group()
                    value = cell.find(NS + 'v')
                    text = value.text if value is not None and value.text is not None else ''
                    kind = cell.attrib.get('t')
                    if kind == 's':
                        text = self.strings[int(text)]
                    elif kind == 'inlineStr':
                        text = ''.join(t.text or '' for t in cell.iter(NS + 't'))
                    if cell.find(NS + 'f') is not None:
                        raise ValueError(f'Formula in assignment sheet {sheet}, cell {cell.attrib["r"]}; use lecturer original values')
                    values[col] = text
                row_number = element.attrib.get('r')
                element.clear()
                if headers is None:
                    if not values:
                        continue
                    headers = {col: text.strip() for col, text in values.items() if text.strip()}
                    if len(set(headers.values())) != len(headers):
                        raise ValueError(f'Duplicate headers in {sheet}')
                    continue
                record = {header: values.get(col, '') for col, header in headers.items()}
                if any(record.values()):
                    record['_row'] = row_number
                    yield record


@dataclass
class Assignment:
    code: str
    course_class: str
    group: int
    city: str
    currency: str
    base_url: str
    snapshots: list
    listing_ids: set
    areas: dict
    review_ids: set
    llm_ids: set
    manual_ids: set
    fingerprint: str


def load_assignment(path, course_class, group):
    path = Path(path)
    fingerprint = sha256(path.read_bytes()).hexdigest()
    book = XlsxReader(path)
    try:
        def belongs(row):
            if row.get('Lớp', '').strip() != course_class:
                return False
            try:
                return identifier(row.get('Nhóm', '')) == str(group)
            except ValueError:
                return False
        matches = [r for r in book.records('Phân công') if belongs(r)]
        if len(matches) != 1:
            raise ValueError(f'Expected one assignment row for {course_class}, group {group}; found {len(matches)}')
        meta = matches[0]
        code = meta['Mã dữ liệu'].strip()
        snapshots = [meta[f'Mốc {i}'].strip() for i in range(1, 5)]
        for snapshot in snapshots:
            if date.fromisoformat(snapshot).isoformat() != snapshot:
                raise ValueError('Snapshot must use YYYY-MM-DD')
        if len(set(snapshots)) != 4 or snapshots != sorted(snapshots):
            raise ValueError('Four unique chronological snapshots required')
        listings, areas, reviews, llm, manual = set(), {}, set(), set(), set()
        for sheet, ids in [('Listing', listings), ('Review', reviews)]:
            for row in book.records(sheet):
                if not belongs(row):
                    continue
                if row['Mã dữ liệu'].strip() != code:
                    raise ValueError(f'Conflicting data code in {sheet}')
                key = identifier(row['listing_id' if sheet == 'Listing' else 'review_id'])
                if key in ids:
                    raise ValueError(f'Duplicate assigned ID in {sheet}: {key}')
                ids.add(key)
                if sheet == 'Listing':
                    areas[key] = row.get('analysis_area', '').strip()
                else:
                    if row.get('Mẫu LLM', '').strip().lower() == 'x':
                        llm.add(key)
                    if row.get('Nhãn tay', '').strip().lower() == 'x':
                        manual.add(key)
        if not listings or not reviews or not manual <= llm <= reviews:
            raise ValueError('Empty ID assignment or manual labels outside LLM sample')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', code):
            raise ValueError('Invalid data code for report filename')
        return Assignment(code, course_class, group, meta['Thành phố'], meta['Tiền tệ'],
                          meta['URL gốc Inside Airbnb'], snapshots, listings, areas,
                          reviews, llm, manual, fingerprint)
    finally:
        book.close()
