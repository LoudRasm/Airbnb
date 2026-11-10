"""Test TV1's integration contract; owners add tests for their own algorithms."""
import contextlib
from contextlib import ExitStack
import csv
import gzip
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src'))
import run_pipeline as pipeline
from airbnb.loading import snapshot_rows


class PipelineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'configs').mkdir()
        self.cfg = json.loads((ROOT / 'configs/toronto.yaml').read_text())
        self.config = self.root / 'configs/toronto.yaml'
        self.config.write_text(json.dumps(self.cfg))
        shutil.copytree(ROOT / 'data/samples/demo', self.root / 'data/samples/demo')
        (self.root / 'data/samples/manual_labels.csv').write_text('review_id,sentiment\n100,positive\n')

    def tearDown(self):
        self.temp.cleanup()

    def test_todo_blocks_before_download_or_output_and_status_works_outside_repo(self):
        with patch.object(pipeline, 'download') as download, contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(pipeline.main(['--config', str(self.config)]), 2)
            download.assert_not_called()
        self.assertIn('TODO', errors.getvalue())
        self.assertFalse((self.root / 'data/processed').exists())
        result = subprocess.run([sys.executable, str(ROOT / 'run_pipeline.py'), '--status'], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for name in ['Mai Anh Đức', 'Nguyễn Quốc Hiếu', 'Vũ Phạm Khánh Nam', 'Phan Ngọc Huy']:
            self.assertIn(name, result.stdout)

    def stage_doubles(self, full=False, bad_kpi=False):
        stack = ExitStack()
        for module in pipeline.CORE_MODULES + pipeline.LLM_MODULES:
            stack.enter_context(patch.object(module, 'READY', True))
        def clean(records, snapshot, cfg):
            return ([{'snapshot_date':snapshot, 'listing_id':r['id'], 'host_id':r['host_id'], 'price':None,
                      'room_type':r['room_type'], 'analysis_area':r.get('analysis_area','DEMO'),
                      'neighbourhood_cleansed':r['neighbourhood_cleansed'], 'latitude':None,
                      'longitude':None, 'qa_flags':''} for r in records], [])
        def collect(records, snapshot, existing):
            for row in records:
                existing.setdefault(row['id'], {'review_id':row['id'],'listing_id':row['listing_id'],
                    'date':row['date'],'comments':row['comments'],'first_seen_snapshot':snapshot})
            return {}
        market={'snapshot_date':self.cfg['snapshots'][-1], 'analysis_area':'DEMO','supply':3,
                'median_price':'','price_n':0,'currency':'CAD','entire_home_share':0.0,'multi_listing_host_share':0.0}
        if bad_kpi: market.pop('currency')
        mocks={}
        operations=[(pipeline.qa,'clean_listings',clean),(pipeline.reviews,'collect',collect),
                    (pipeline.calendar,'aggregate',lambda *a:([],{})),(pipeline.calendar,'metrics',lambda *a:[]),
                    (pipeline.kpi,'summarize',lambda *a:[market]),(pipeline.analysis,'churn',lambda *a:[]),
                    (pipeline.eda,'profile',lambda *a:[]),
                    (pipeline.baseline,'predict',lambda r:{'review_id':r['review_id'],'sentiment':'positive','source':'test_double'})]
        for module, name, implementation in operations:
            mocks[name]=stack.enter_context(patch.object(module, name, side_effect=implementation))
        for module in [pipeline.viz_market,pipeline.viz_qa,pipeline.viz_spatial,pipeline.viz_calendar,pipeline.viz_reviews]:
            mocks[module.__name__]=stack.enter_context(patch.object(module,'render',return_value=[]))
        if full:
            prediction={'review_id':'100','sentiment':'positive','language':'en','positive_aspects':['host'],'negative_aspects':[],'source':'test_double'}
            mocks['analyze']=stack.enter_context(patch.object(pipeline.llm,'analyze',return_value=[prediction]))
            mocks['guest_kpi']=stack.enter_context(patch.object(pipeline.review_kpi,'guest_kpi',return_value=[]))
            mocks['evaluate']=stack.enter_context(patch.object(pipeline.evaluate,'evaluate',return_value=[]))
        return stack, mocks

    def test_imported_owner_functions_are_called_and_outputs_written(self):
        stack, mocks = self.stage_doubles()
        with stack, contextlib.redirect_stdout(io.StringIO()):
            pipeline.run(self.config, demo=True, skip_llm=True)
        self.assertEqual(mocks['clean_listings'].call_count,4)
        self.assertEqual(mocks['aggregate'].call_count,4)
        self.assertEqual(mocks['collect'].call_count,4)
        self.assertEqual(mocks['predict'].call_count,3)
        self.assertTrue((self.root/'data/processed/demo/kpi_market.csv').exists())
        mocks['airbnb.viz_reviews'].assert_not_called()

    def test_full_wiring_passes_assigned_llm_ids_and_evaluates_same_review_ids(self):
        shutil.copytree(self.root/'data/samples/demo',self.root/'data/raw')
        ids={str(i) for i in range(1,7)}
        assigned=SimpleNamespace(listing_ids=ids,review_ids={'100','101','102'},areas={i:'A01' for i in ids},
                                 llm_ids={'100'},manual_ids={'100'})
        stack,mocks=self.stage_doubles(full=True)
        with stack, patch.object(pipeline,'read_assignment',return_value=assigned), contextlib.redirect_stdout(io.StringIO()):
            pipeline.run(self.config,skip_llm=False,no_download=True)
        self.assertEqual(mocks['analyze'].call_args.args[-1],{'100'})
        self.assertEqual(mocks['evaluate'].call_count,2)
        for call in mocks['evaluate'].call_args_list:
            self.assertEqual({r['review_id'] for r in call.args[0]},{'100'})
            self.assertEqual({r['review_id'] for r in call.args[1]},{'100'})
        mocks['airbnb.viz_reviews'].assert_called_once()
        with (self.root/'data/processed/real/llm_reviews.csv').open() as stream:
            row=next(csv.DictReader(stream))
        self.assertEqual(json.loads(row['positive_aspects']),['host'])

    def test_bad_member_schema_is_rejected_before_writing(self):
        stack,_=self.stage_doubles(bad_kpi=True)
        with stack:
            with self.assertRaisesRegex(ValueError,'currency'):
                pipeline.run(self.config,demo=True,skip_llm=True)
        self.assertFalse((self.root/'data/processed').exists())

    def test_loading_uses_review_id_not_listing_id_and_preserves_large_ids(self):
        folder=self.root/'data/raw'/self.cfg['snapshots'][0];folder.mkdir(parents=True)
        large='1502977270045215452'
        with gzip.open(folder/'reviews.csv.gz','wt',newline='') as stream:
            w=csv.writer(stream);w.writerow(['id','listing_id','date','comments'])
            w.writerows([[large,'999','2025-08-01','Assigned review with other listing'],['7','1','2025-08-01','Unassigned review']])
        assigned=SimpleNamespace(review_ids={large},listing_ids={'1'},areas={'1':'A01'})
        records=list(snapshot_rows(self.root,self.cfg,self.cfg['snapshots'][0],'reviews.csv.gz',assigned))
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['id'],large)
        self.assertEqual(records[0]['listing_id'],'999')


if __name__ == '__main__':
    unittest.main()
