"""Invented-data oracles and complete final evaluation/recovery checks."""

import copy
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from jsonschema import ValidationError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_browser_inference import check
from compare_final_runs import compare_final, verified_final
from evaluate_final import evaluate
from final_inputs import CRITICAL, historical_compatibility, inputs
from final_release import release_checks
from final_statistics import interval, match_weights
from ingest_statsbomb import AuditError, canonical, sha256
from prepare_training import prepare
from report_final import validate_final, verify_views
from run_io import PROJECT, code_identity, read_json
from train_models import train
from test_training import dataset, resign, write_features


def sign_evidence(e):
    clean={k:v for k,v in e.items() if k!='evidence_id'}
    e['evidence_id']=sha256(canonical(clean).encode())
    return e


class BootstrapOracleTests(unittest.TestCase):
    def test_whole_match_multiplicity_and_shot_weighting(self):
        group=np.array([0,0,1])
        draws=np.array([[2,0],[1,1],[0,2],[0,2]])
        v=np.array([0.,0.,1.])
        result=interval(v,np.array([True]*3),group,draws,.5)
        self.assertAlmostEqual(result['estimate'],1/3)
        np.testing.assert_allclose(result['interval'],[.25,1.])
        # Selecting a two-match slice with skipped draws keeps their count explicit.
        group=np.array([0,1,2]);draws=np.array([[3,0,0],[0,3,0],[0,0,3]])
        result=interval(np.array([0.,1.,9.]),np.array([True,True,False]),group,draws,.95)
        self.assertEqual((result['valid_resamples'],result['skipped_resamples']),(2,1))
        single=interval(np.array([0.,1.,9.]),np.array([True,False,False]),group,draws,.95)
        self.assertIsNone(single['interval'])

    def test_deterministic_draws_and_historical_compatibility(self):
        config=read_json(PROJECT/'model/final-evaluation-protocol.json')
        rows=[{'match_id':1},{'match_id':1},{'match_id':2}]
        a,b=match_weights(rows,config)
        c,d=match_weights(rows,config)
        np.testing.assert_array_equal(a,c);np.testing.assert_array_equal(b,d)
        manifest={'code_sha256':code_identity()}
        historical_compatibility(manifest)
        # New evaluator/report files are not a reason to refit the historical model.
        for key in list(manifest['code_sha256']):
            if key not in CRITICAL:manifest['code_sha256'].pop(key)
        historical_compatibility(manifest)
        manifest['code_sha256']['scripts/xg/features.py']='0'*64
        with self.assertRaisesRegex(AuditError,'semantics'):historical_compatibility(manifest)


class FinalWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        write_features(cls.root/'features',dataset())
        cls.prepared=prepare(cls.root/'features',cls.root/'prepared')
        cls.training=train(cls.prepared,cls.root/'training')
        cls.parity=check(cls.training,cls.root/'parity')
        cls.first=evaluate(cls.prepared,cls.training,cls.parity,cls.root/'final-first')
        cls.e=read_json(cls.first/'final-evaluation.json')

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_complete_reproduction_and_generated_views(self):
        other=evaluate(self.prepared,self.training,self.parity,self.root/'final-repeat')
        result=compare_final(self.first,other)
        self.assertEqual(result['files_verified'],8)
        self.assertEqual(result['byte_differences'],[])
        self.assertEqual(verify_views(self.first),self.e)
        self.assertEqual(self.e['test_status'],'opened-final-evaluation')
        self.assertEqual(self.e['development_evidence']['test_status'],'unopened')
        self.assertFalse(self.e['release_checks']['publication_authorized'])
        # This invented fixture has only 48 test matches: completed withheld evidence.
        self.assertEqual(self.e['release_checks']['status'],'withheld')
        self.assertFalse(self.e['release_checks']['predicates']['test_support'])
        self.assertTrue(list((self.prepared.parent/'.final-test-access').glob('test-opened-*.json')))
        self.assertTrue(list((self.root/'final-first').glob('test-opened-*.json')))
        verified_final(self.first)

    def test_release_boundaries_never_switch_candidate(self):
        e=copy.deepcopy(self.e)
        e['test_summary'].update(matches=100,shots=1000,goals=200)
        e['scene_audit']['responses']={'keeper':True,'defender':True};e['scene_audit']['invariants_pass']=True
        for name in ('selected_minus_constant','selected_minus_full_logistic'):
            for metric in ('log_loss','brier'):
                e['paired'][name][metric].update(estimate=-.01,interval=[-.02,-.001])
        result=release_checks(e)
        self.assertEqual(result['status'],'needs_review');self.assertFalse(result['publication_authorized'])
        e['paired']['selected_minus_constant']['log_loss']['interval'][1]=0
        self.assertEqual(release_checks(e)['status'],'withheld')
        e['paired']['selected_minus_constant']['log_loss']['interval'][1]=-.001
        e['paired']['selected_minus_full_logistic']['brier']['estimate']=.00011
        self.assertEqual(release_checks(e)['status'],'withheld')
        self.assertEqual(e['development_evidence']['selection'],self.e['development_evidence']['selection'])

    def test_privacy_unknown_fields_and_identity(self):
        for key,value in [('match_ids',[1]),('parameters',{}),('anything',[])]:
            e=copy.deepcopy(self.e);e[key]=value;sign_evidence(e)
            with self.assertRaises(ValidationError):validate_final(e)
        e=copy.deepcopy(self.e);e['results'][0]['calibration_bins'][0]['vector']=[1]
        sign_evidence(e)
        with self.assertRaises(ValidationError):validate_final(e)
        e=copy.deepcopy(self.e);e['evidence_id']='0'*64
        with self.assertRaises(AuditError):validate_final(e)

    def test_failures_before_and_after_opening(self):
        bad=self.root/'bad-parity';bad.mkdir()
        for path in self.parity.iterdir():(bad/path.name).write_bytes(path.read_bytes())
        p=read_json(bad/'parity.json');p['training_run_id']='0'*64
        (bad/'parity.json').write_text(canonical(p));resign(bad)
        with self.assertRaises(AuditError):evaluate(self.prepared,self.training,bad,self.root/'never-opened')
        self.assertFalse((self.root/'never-opened').exists())
        with self.assertRaises(AuditError):evaluate(self.training,self.training,self.parity,self.root/'wrong-phase')
        with patch('evaluate_final.test_rows',side_effect=AuditError('invented failure after opening')):
            with self.assertRaises(AuditError):evaluate(self.prepared,self.training,self.parity,self.root/'interrupted')
        self.assertTrue(list((self.root/'interrupted').glob('test-opened-*.json')))
        self.assertFalse(list((self.root/'interrupted').glob('*/manifest.json')))
        recovered=evaluate(self.prepared,self.training,self.parity,self.root/'interrupted')
        self.assertEqual(recovered.name,self.first.name)

    def test_membership_and_hash_failures(self):
        with self.assertRaises(AuditError):compare_final(self.first,self.first)
        with self.assertRaises(AuditError):compare_final(self.prepared,self.first)
        changed=self.root/'corrupt';changed.mkdir()
        for path in self.first.iterdir():(changed/path.name).write_bytes(path.read_bytes())
        (changed/'methodology.md').write_text('corrupt')
        with self.assertRaises(AuditError):verified_final(changed)
        resign(changed)
        with self.assertRaisesRegex(AuditError,'differs from evidence'):verified_final(changed)
        context=inputs(self.prepared,self.training,self.parity)
        context['split']=copy.deepcopy(context['split'])
        mid=next(k for k,v in context['split'].items() if v=='test');context['split'][mid]='train'
        from final_inputs import test_rows
        with self.assertRaisesRegex(AuditError,'membership'):test_rows(context)


if __name__=='__main__':unittest.main()
