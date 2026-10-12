"""Behavior oracles and a complete invented-data research/holdout workflow."""

import copy
import math
import shutil
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from behavior_holdout import evaluate_fresh, reserve, usage_declaration
from behavior_io import original_inputs, research_protocol
from behavior_statistics import gates, select_candidates
from behavior_sweeps import (boundary_cases, direction_summary, evaluate_sweeps, physical_cases,
                             response_summary)
from check_browser_inference import verify
from compare_behavior_runs import compare_behavior, verified_research
from features import extract_metric_features
from ingest_statsbomb import AuditError, canonical
from model_export import calibration_apply, predict_envelope, seal
from prepare_training import prepare
from report_behavior import evidence_identity, render_report, validate_behavior
from run_io import PROJECT, read_json
from train_models import train
from training import estimator
from test_training import dataset, resign, write_features


class BehaviorOracleTests(unittest.TestCase):
    def test_directions_plateaus_and_rounded_output(self):
        self.assertEqual(direction_summary([.24,.32], -1, 1e-7)['violations'], 1)
        self.assertEqual(direction_summary([.3,.2,.2], -1, 1e-7)['violations'], 0)
        self.assertEqual(direction_summary([.1,.10000005], -1, 1e-7)['violations'], 0)
        result = response_summary([.1,.1,.1,.2,.2], [0,1,2,3,4], 1e-7, .02)
        self.assertEqual(result['longest_plateau_span'], 2)
        self.assertEqual(result['plateau_share'], .75)
        self.assertEqual(result['large_jump_rate'], .25)
        masked = response_summary([.1,.1,.1], [0,1,2], 1e-7, .02, [True,False])
        self.assertEqual(masked['longest_plateau_span'], 1)
        # Same displayed two-decimal probability does not establish a plateau.
        self.assertEqual(response_summary([.101,.104], [0,1], 1e-7, .02)['plateau_share'], 0)
        p=calibration_apply([.1,.2,.3], {'method':'sigmoid','slope':2.,'intercept':-1.,'clip':1e-12})
        self.assertEqual(direction_summary(p, 1, 1e-7)['violations'],0)

    def test_physical_coupling_cone_boundary_and_constraint_mapping(self):
        config=research_protocol()
        paths={p['name']:p for p in physical_cases(config)}
        v=paths['central_shooter']['vectors']
        self.assertGreater(v[0,0],v[-1,0])
        self.assertLess(v[0,1],v[-1,1])
        self.assertNotEqual(v[0,7],v[-1,7])
        values=[extract_metric_features(c['scene'])['vector'] for c in boundary_cases()[:3]]
        self.assertEqual([v[4] for v in values],[1,1,0])
        mono=estimator(config['candidate'], {'max_depth':2,'learning_rate':.05,'min_child_weight':20},
                       config['original_training_protocol'])
        self.assertEqual(mono.get_params()['monotone_constraints'],(-1,1,0,0,0,0,0,0))
        experiment=copy.deepcopy(config['candidate']);experiment['indices'].reverse()
        with self.assertRaises(AuditError):estimator(experiment,{},config['original_training_protocol'])
        old=config['original_training_protocol']['experiments'][-1]
        self.assertIsNone(estimator(old,{},config['original_training_protocol']).get_params()['monotone_constraints'])

    def test_selection_bounds_and_no_primary_support(self):
        config=research_protocol()
        current={'pooled':{'primary':{'pairs':100,'p95_jump':.02,'large_jump_rate':.1}}}
        record={'quality':{'paired_with_current':{'log_loss':{'upper_95':.005},'brier':{'upper_95':.001}},
                          'beats_constant':True,'calibration_bins':[],'slices':[]},
                'behavior':{'partial_direction_pass':True,'pooled':{'primary':{'pairs':100,'p95_jump':.01,'large_jump_rate':.05}}},
                'scene_audit':{'invariants_pass':True},'parity':{'status':'pass'},'native_export_pass':True}
        self.assertTrue(gates(record,current,config)['eligible'])
        records={n:{'gates':gates(record,current,config)} for n in config['decision']['order']}
        self.assertEqual(select_candidates(records,config)['recommended_model'],'full_logistic')
        broken=copy.deepcopy(record);broken['quality']['paired_with_current']['log_loss']['upper_95']=.0050001
        self.assertFalse(gates(broken,current,config)['eligible'])
        for key in ('native_export_pass',):
            broken=copy.deepcopy(record);broken[key]=False
            self.assertFalse(gates(broken,current,config)['eligible'])
        broken=copy.deepcopy(record);broken['behavior']['pooled']['primary']['pairs']=0
        self.assertFalse(gates(broken,current,config)['predicates']['primary_segments_available'])
        zero=copy.deepcopy(current);zero['pooled']['primary'].update(large_jump_rate=0,p95_jump=0)
        flat=copy.deepcopy(record);flat['behavior']['pooled']['primary'].update(large_jump_rate=0,p95_jump=0)
        self.assertFalse(gates(flat,zero,config)['eligible'])
        for r in records.values():r['gates']['eligible']=False
        self.assertEqual(select_candidates(records,config)['status'],'retain_current')

    def test_ledger_requires_every_historical_partition(self):
        declaration={'prior_use_complete':True,'outcomes_not_used_for_choice':True,
                     'prior_match_ids':[1,2,3], 'eligibility':'Invented test cohort'}
        with self.assertRaises(AuditError):usage_declaration(declaration, {'1':'train','4':'test'})
        self.assertEqual(usage_declaration(declaration, {'1':'train','2':'test'}),{1,2,3})
        declaration['outcomes_not_used_for_choice']=False
        with self.assertRaises(AuditError):usage_declaration(declaration, {'1':'train'})

    def test_logistic_sign_oracle_and_research_model_browser_mapping(self):
        fixture=read_json(PROJECT/'tests/fixtures/inference-models.json')[0]['envelope']
        config=research_protocol()
        final=read_json(PROJECT/'model/final-evaluation-protocol.json')
        fixture=copy.deepcopy(fixture)
        fixture['model_version']='full_logistic';fixture['feature_indices']=list(range(8))
        fixture['parameters']={'kind':'logistic','mean':[0.]*8,'scale':[1.]*8,
                               'coefficients':[-.1,.02,0.,0.,0.,0.,0.,0.],'intercept':-1.}
        fixture=seal(fixture)
        result,_=evaluate_sweeps(fixture, dataset(2,10),config,final)
        self.assertTrue(result['partial_direction_pass'])
        fixture['parameters']['coefficients'][0]=.1
        result,_=evaluate_sweeps(seal(fixture),dataset(2,10),config,final)
        self.assertFalse(result['partial_direction_pass'])
        fixture=copy.deepcopy(read_json(PROJECT/'tests/fixtures/inference-models.json')[-1]['envelope'])
        fixture['model_version']='full_monotonic_xgboost';fixture=seal(fixture)
        self.assertEqual(verify(fixture)['status'],'pass')


class BehaviorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        write_features(cls.root/'features',dataset())
        cls.prepared=prepare(cls.root/'features',cls.root/'prepared')
        cls.training=train(cls.prepared,cls.root/'training')
        cls.published=cls.training/'full_xgboost.json'
        # Synthetic original selection may favor logistic. This test constructs an
        # internally consistent historical XGBoost disposition, with no real rows.
        selection=read_json(cls.training/'selection.json')
        model=read_json(cls.published)
        selection.update(status='frozen_candidate',selected_model='full_xgboost',selected_artifact_id=model['artifact_id'])
        (cls.training/'selection.json').write_text(canonical(selection))
        e=read_json(cls.training/'evaluation.json');e['selection']=selection
        (cls.training/'evaluation.json').write_text(canonical(e))
        (cls.training/'selected-model.json').write_bytes(cls.published.read_bytes())
        manifest=read_json(cls.training/'manifest.json');manifest['selected_model']='full_xgboost'
        (cls.training/'manifest.json').write_text(canonical(manifest));resign(cls.training)
        # Original run linkage is retained; the re-signed test folder identity is valid.
        cls.original_read=Path.read_bytes
        rows=dataset(60,15)
        for r in rows:r['match_id']+=1000;r['event_id']='fresh-'+r['event_id']
        write_features(cls.root/'fresh-features',rows)
        declaration={'prior_use_complete':True,'outcomes_not_used_for_choice':True,
                     'prior_match_ids':list(range(1,241)), 'eligibility':'Invented unused matches only'}
        (cls.root/'usage.json').write_text(canonical(declaration))
        with patch.multiple('behavior_io', PUBLISHED=cls.published, REVIEWED_TRAINING=cls.training/'manifest.json'):
            cls.reservation=reserve(cls.prepared,cls.training,cls.root/'fresh-features',cls.root/'usage.json',cls.root/'reserved')
        from evaluate_behavior import evaluate
        def no_test_parse(path):
            if path.name=='test.jsonl':raise AssertionError('Original final test must not be parsed')
            return cls.original_read(path)
        with patch.multiple('behavior_io', PUBLISHED=cls.published, REVIEWED_TRAINING=cls.training/'manifest.json'),patch.object(Path,'read_bytes',no_test_parse):
            cls.first=evaluate(cls.prepared,cls.training,cls.root/'first',reservation_dir=cls.reservation)
            cls.second=evaluate(cls.prepared,cls.training,cls.root/'second',reservation_dir=cls.reservation)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_complete_immutable_reproduction_and_parity(self):
        result=compare_behavior(self.first,self.second)
        self.assertEqual(result['files_verified'],12)
        self.assertEqual(result['byte_differences'],[])
        root,_,e=verified_research(self.first)
        self.assertFalse(e['selection']['publication_authorized'])
        self.assertEqual(e['previous_final_test'],'already_opened_not_parsed')
        self.assertEqual(e['native_export']['directions']['native_raw']['violations'],0)
        self.assertTrue(all(r['parity']['status']=='pass' for r in e['models'].values()))
        self.assertEqual((root/'comparison.md').read_bytes(),render_report(e))
        for name in ('current-model.json','logistic-model.json'):
            original='selected-model.json' if name=='current-model.json' else 'full_logistic.json'
            self.assertEqual((root/name).read_bytes(),(self.training/original).read_bytes())
        bad=copy.deepcopy(e);bad['models']['full_xgboost']['quality']['match_ids']=[1]
        bad['evidence_id']=evidence_identity(bad)
        with self.assertRaises(AuditError):validate_behavior(bad)
        with self.assertRaises(AuditError):compare_behavior(self.first,self.first)

    def test_overlap_and_integrity_fail_before_training(self):
        with patch.multiple('behavior_io', PUBLISHED=self.published, REVIEWED_TRAINING=self.training/'manifest.json'):
            with self.assertRaisesRegex(AuditError,'overlaps'):
                reserve(self.prepared,self.training,self.root/'features',self.root/'usage.json',self.root/'bad')
        from evaluate_behavior import evaluate
        copy_root=self.root/'damaged';copy_root.mkdir()
        for p in self.prepared.iterdir():(copy_root/p.name).write_bytes(p.read_bytes())
        (copy_root/'selection.jsonl').write_text('corrupt')
        with self.assertRaises(AuditError):evaluate(copy_root,self.training,self.root/'failed')
        self.assertFalse((self.root/'failed').exists())

    def test_reviewed_reference_identity_rejects_resigned_mutation(self):
        altered = self.root/'resigned-reference'
        shutil.copytree(self.training, altered)
        (altered/'constant-reference.json').write_text(canonical({'probability': .5, 'fitted_partition': 'train'}))
        resign(altered)
        with patch.multiple('behavior_io', PUBLISHED=self.published, REVIEWED_TRAINING=self.training/'manifest.json'):
            with self.assertRaisesRegex(AuditError, 'exact reviewed reference'):
                original_inputs(self.prepared, altered, research_protocol())

    def test_failure_after_opening_keeps_access_record(self):
        root, rm, original = verified_research(self.first)
        e = copy.deepcopy(original)
        e['selection']['recommended_model'] = 'full_logistic'
        isolated = self.root/'failed-holdout'/self.reservation.name
        shutil.copytree(self.reservation, isolated)
        with patch('behavior_holdout.verified_research', return_value=(root, rm, e)):
            with patch('behavior_holdout.matches', side_effect=AuditError('Invented post-access failure')):
                with self.assertRaisesRegex(AuditError, 'post-access failure'):
                    evaluate_fresh(self.first, isolated, self.root/'failed-fresh')
            self.assertTrue(list((isolated.parent/'.behavior-test-access').glob('opened-*.json')))
            with self.assertRaisesRegex(AuditError, 'already opened'):
                evaluate_fresh(self.first, isolated, self.root/'retry-fresh')
        self.assertFalse((self.root/'failed-fresh').exists())

    def test_once_opened_frozen_evaluation_without_refit(self):
        root, rm, original = verified_research(self.first)
        e = copy.deepcopy(original)
        # Reach the access boundary even when the invented candidate cannot pass
        # every product gate. This does not create real model-selection evidence.
        e['selection']['recommended_model'] = 'full_logistic'
        isolated = self.root/'isolated-holdout'/self.reservation.name
        shutil.copytree(self.reservation, isolated)
        with patch('behavior_holdout.verified_research', return_value=(root, rm, e)):
            result = evaluate_fresh(self.first, isolated, self.root/'forced-fresh')
            fresh = read_json(result/'fresh-evaluation.json')
            self.assertFalse(fresh['publication_authorized'])
            self.assertEqual(fresh['test_status'], 'opened_once')
            with self.assertRaisesRegex(AuditError, 'already opened'):
                evaluate_fresh(self.first, isolated, self.root/'forced-repeat')
        # Keep other tests independent while retaining the original once-opened
        # marker: the no-candidate path must not create a second access record.

    def test_fresh_access_boundary_and_no_candidate(self):
        e=read_json(self.first/'behavior-evaluation.json')
        before = list((self.reservation.parent/'.behavior-test-access').glob('*'))
        if e['selection']['recommended_model'] is None:
            with self.assertRaisesRegex(AuditError,'No frozen alternative'):
                evaluate_fresh(self.first,self.reservation,self.root/'test')
            self.assertEqual(list((self.reservation.parent/'.behavior-test-access').glob('*')), before)
        else:
            result=evaluate_fresh(self.first,self.reservation,self.root/'test')
            fresh=read_json(result/'fresh-evaluation.json')
            self.assertFalse(fresh['publication_authorized'])
            with self.assertRaisesRegex(AuditError,'already opened'):
                evaluate_fresh(self.first,self.reservation,self.root/'test-repeat')


if __name__=='__main__':unittest.main()
