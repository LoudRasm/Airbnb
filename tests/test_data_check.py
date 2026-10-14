"""End-to-end checks with a tiny original-style XLSX and raw gzip fixtures."""
import csv
from datetime import date
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest
from xml.sax.saxutils import escape
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from airbnb.assignment import load_assignment, identifier
from airbnb.data_check import PARTS, context, run_part, merge

DATES = ['2025-09-11', '2025-12-12', '2026-03-19', '2026-06-15']
LARGE_ID = '1502977270045215452'
CODE = 'DSE2049-C01-G10-toronto'


def worksheet(rows):
    parts = ['<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for i, row in enumerate(rows, 1):
        parts.append(f'<row r="{i}">')
        for j, value in enumerate(row):
            col = chr(ord('A')+j)
            if value is not None:
                parts.append(f'<c r="{col}{i}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
        parts.append('</row>')
    return ''.join(parts) + '</sheetData></worksheet>'


def assignment_xlsx(path):
    sheets = {
        'Phân công': [['Lớp','Nhóm','Thành phố','Quốc gia','Tiền tệ','Mã dữ liệu','Mốc 1','Mốc 2','Mốc 3','Mốc 4','URL gốc Inside Airbnb'],
                     ['UET.DSE2049 1',10,'Toronto','Canada','CAD',CODE,*DATES,'https://data.insideairbnb.com/canada/on/toronto/']],
        'Listing': [['Lớp','Nhóm','Mã dữ liệu','listing_id','analysis_area'],
                    ['UET.DSE2049 1',10,CODE,LARGE_ID,'A01'],['UET.DSE2049 1',10,CODE,'2','A02'],
                    ['UET.DSE2049 2',10,'other','9','A01']],
        'Review': [['Lớp','Nhóm','Mã dữ liệu','review_id','listing_id','Mẫu LLM','Nhãn tay'],
                   ['UET.DSE2049 1',10,CODE,'100',LARGE_ID,'x','x'],
                   ['UET.DSE2049 1',10,CODE,'101','999','x',None]],
    }
    with ZipFile(path, 'w') as z:
        names = list(sheets)
        z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' + ''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i,name in enumerate(names,1)) + '</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(names)+1)) + '</Relationships>')
        for i, rows in enumerate(sheets.values(),1):
            z.writestr(f'xl/worksheets/sheet{i}.xml',worksheet(rows))


def raw_csv(path, fields, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path,'wt',encoding='utf-8',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(fields);writer.writerows(records)


class AssignedChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/'configs').mkdir()
        assignment_xlsx(self.root/'assignment.xlsx')
        cfg={'course_class':'UET.DSE2049 1','group':10,'data_code':CODE,'assignment':'assignment.xlsx',
             'raw':'data/raw','output':'reports/checks','expected':{'listings':2,'reviews':2,'llm':2,'manual':1,
             'calendar_days_per_listing':1,'entire_home':1,'private_room':1,'no_reviews':[1]*4,'missing_price_last':1}}
        (self.root/'configs/data_check.json').write_text(json.dumps(cfg))
        self.root,self.cfg,self.assignment=context(self.root/'configs/data_check.json')
        for i,snapshot in enumerate(DATES):
            folder=self.root/'data/raw'/snapshot
            raw_csv(folder/'listings.csv.gz',['id','room_type','number_of_reviews','price','empty'],
                    [[LARGE_ID,'Entire home/apt','0','' if i<3 else '$100.00',''],['2','Private room','1','',''],['9','Private room','0','$20.00','']])
            raw_csv(folder/'calendar.csv.gz',['listing_id','date','available'],[[LARGE_ID,snapshot,'t'],['2',snapshot,'f'],['9',snapshot,'t']])
            # Assigned review 101 has a listing_id outside the assigned listings; it must still be kept.
            raw_csv(folder/'reviews.csv.gz',['id','listing_id','date','comments'],[['100',LARGE_ID,snapshot,'Great'],['101','999',snapshot,'Bad'],['999',LARGE_ID,snapshot,'Not assigned']])

    def tearDown(self):
        self.temp.cleanup()

    def run_all(self):
        for part in PARTS:
            self.assertTrue(run_part(self.root,self.cfg,self.assignment,part))
        return merge(self.root,self.cfg,self.assignment)

    def test_valid_flow_and_review_id_filter_preserves_each_snapshot(self):
        self.assertTrue(self.run_all())
        out=self.root/'reports/checks'
        with (out/f'check_{CODE}.csv').open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4)
        self.assertEqual([r['ngay'] for r in rows],DATES)
        self.assertTrue(all(r['reviews_dong']=='2' for r in rows))
        self.assertTrue(all(r['calendar_dong']=='2' for r in rows))
        self.assertEqual([r['thieu_price'] for r in rows],['2','2','2','1'])
        self.assertEqual(len(self.assignment.llm_ids),2)
        self.assertEqual(len(self.assignment.manual_ids),1)
        self.assertIn(LARGE_ID,self.assignment.listing_ids)
        self.assertEqual(identifier(LARGE_ID),LARGE_ID)
        self.assertEqual(identifier('1.502977270045215452E18'),LARGE_ID)
        self.assertTrue((out/'report_answers.md').exists())

    def test_bad_dates_report_error_and_continue_all_four_snapshots(self):
        path=self.root/'data/raw'/DATES[0]/'calendar.csv.gz'
        raw_csv(path,['listing_id','date','available'],[[LARGE_ID,'invalid','t'],['2','invalid','f']])
        self.assertFalse(run_part(self.root,self.cfg,self.assignment,'calendar'))
        with (self.root/'reports/checks/calendar_summary.csv').open() as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]['invalid_date_rows'],'2')
        self.assertEqual(rows[-1]['status'],'ok')

    def test_missing_part_blocks_submission_and_missing_file_is_not_zero(self):
        path=self.root/'data/raw'/DATES[0]/'calendar.csv.gz';path.unlink()
        self.assertFalse(run_part(self.root,self.cfg,self.assignment,'calendar'))
        self.assertFalse(merge(self.root,self.cfg,self.assignment))
        out=self.root/'reports/checks'
        with (out/'calendar_summary.csv').open() as f:
            first=next(csv.DictReader(f))
        self.assertEqual(first['calendar_dong'],'')
        self.assertFalse((out/f'check_{CODE}.csv').exists())
        self.assertTrue((out/f'check_{CODE}.draft.csv').exists())

    def test_stale_raw_or_workbook_cannot_be_merged(self):
        self.assertTrue(self.run_all())
        path=self.root/'data/raw'/DATES[0]/'reviews.csv.gz'
        raw_csv(path,['id','listing_id','date','comments'],[['100','2',DATES[0],'Changed']])
        self.assertFalse(merge(self.root,self.cfg,self.assignment))
        self.assertFalse((self.root/'reports/checks'/f'check_{CODE}.csv').exists())
        row_path=self.root/'reports/checks/listings_summary.csv'
        text=row_path.read_text().replace(self.assignment.fingerprint,'wrong-workbook')
        row_path.write_text(text)
        self.assertFalse(merge(self.root,self.cfg,self.assignment))

    def test_changed_counts_or_missing_column_report_block_merge(self):
        self.assertTrue(self.run_all())
        out=self.root/'reports/checks'
        path=out/'reviews_summary.csv'
        with path.open() as stream:
            reader=csv.DictReader(stream); fields=reader.fieldnames; rows=list(reader)
        rows[0]['reviews_dong']='999'
        with path.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)
        self.assertFalse(merge(self.root,self.cfg,self.assignment))
        self.assertTrue(run_part(self.root,self.cfg,self.assignment,'reviews'))
        (out/'missing_columns.csv').unlink()
        self.assertFalse(merge(self.root,self.cfg,self.assignment))

    def test_duplicate_listing_or_calendar_keys_are_not_silently_cleaned(self):
        folder=self.root/'data/raw'/DATES[0]
        raw_csv(folder/'calendar.csv.gz',['listing_id','date','available'],[[LARGE_ID,DATES[0],'t'],[LARGE_ID,DATES[0],'t']])
        self.assertFalse(run_part(self.root,self.cfg,self.assignment,'calendar'))
        with (self.root/'reports/checks/calendar_summary.csv').open() as f:
            row=next(csv.DictReader(f))
        self.assertEqual(row['calendar_dong'],'2')
        self.assertEqual(row['duplicate_keys'],'1')
        self.assertEqual(row['missing_ids_count'],'1')


if __name__ == '__main__':
    unittest.main()
