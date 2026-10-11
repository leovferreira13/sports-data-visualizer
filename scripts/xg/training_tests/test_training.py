import copy
import json
import math
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_runs import compare_runs
from compare_training_runs import compare_training, compare_json
from evaluation import bins, explore, metrics, paired_difference
from features import CONTRACT_PATH, FEATURE_NAMES, extract_metric_features
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import export_estimator, predict_envelope, seal, validate_envelope
from prepare_training import prepare, split_matches
from report_training import render_report, validate_evaluation
from run_io import code_identity, protocol, read_json
from train_models import train, verify_parity
from training import arrays, choose_calibration, configurations, estimator, fit, select, tune


def dataset(matches=240, shots=50):
    rng = random.Random(9)
    result = []
    for mid in range(1, matches + 1):
        for i in range(shots):
            x = 60 + rng.random() * 44
            y = 20 + rng.random() * 28
            scene = {"contract_version": "positional-features/v1", "shot_type": "open-play",
                     "shooter": {"x": x, "y": y}, "goalkeepers": [{"x": 100 + rng.random()*4, "y": 32+rng.random()*4}],
                     "defenders": [{"x": 70 + rng.random()*33, "y": 20 + rng.random()*28},
                                   {"x": 70 + rng.random()*33, "y": 20 + rng.random()*28}], "observation": "embedded-frame"}
            features = extract_metric_features(scene)
            p = 1 / (1 + math.exp(-(-3.6 + (x - 60) / 11)))
            result.append({"competition_id": 1 + (mid - 1)//80, "season_id": 1, "match_id": mid,
                           "event_id": f"invented-{mid}-{i}", "is_goal": int(rng.random() < p), **features})
    return result


def write_features(root, rows):
    root.mkdir()
    data = "".join(canonical(r) for r in rows).encode()
    totals = {"accepted_shots": len(rows), "accepted_goals": sum(r['is_goal'] for r in rows),
              "represented_matches": len({r['match_id'] for r in rows}),
              "shooter_outside_ui_bounds": 0, "represented_scene_outside_ui_bounds": 0}
    audit = canonical({"totals": totals}).encode()
    manifest = {"schema_version":1,"complete":True,"contract_version":"positional-features/v1",
                "code_sha256":{k:v for k,v in code_identity().items() if k in ("model/feature-contract.json", "scripts/xg/extract_features.py", "scripts/xg/features.py", "scripts/xg/ingest_statsbomb.py")},
                "ingestion":{"source_revision":"synthetic-only","source_url":"invented-test-data"},
                "outputs":{"features.jsonl":sha256(data),"feature-audit.json":sha256(audit)}}
    manifest['run_id']=sha256(canonical(manifest).encode())
    (root/'features.jsonl').write_bytes(data)
    (root/'feature-audit.json').write_bytes(audit)
    (root/'manifest.json').write_text(canonical(manifest))


def resign(root):
    m=read_json(root/'manifest.json')
    m.pop('run_id')
    m['outputs']={name:sha256((root/name).read_bytes()) for name in m['outputs']}
    m['run_id']=sha256(canonical(m).encode())
    (root/'manifest.json').write_text(canonical(m))


class ProbabilityTests(unittest.TestCase):
    def test_metrics_bins_and_cluster_bootstrap_oracles(self):
        config=protocol()
        m=metrics([0,1], [0.2,0.8], config)
        self.assertAlmostEqual(m['log_loss'],-math.log(.8))
        self.assertAlmostEqual(m['brier'],.04)
        b=bins([0,1],[0,1],config)
        self.assertEqual((b[0]['shots'],b[9]['shots']),(1,1))
        self.assertIsNone(b[1]['observed_rate'])
        rows=[{'match_id':1},{'match_id':1},{'match_id':2}]
        d=paired_difference(rows,[0,1,1],[.2,.8,.8],[.5,.5,.5],config)
        self.assertAlmostEqual(d['log_loss']['difference'], -math.log(.8)+math.log(.5))
        self.assertEqual(d,paired_difference(rows,[0,1,1],[.2,.8,.8],[.5,.5,.5],config))
        with self.assertRaises(AuditError):metrics([0,1],[float('nan'),.8],config)

    def test_tree_tie_order_and_degenerate_correlations(self):
        config = protocol()
        grid = configurations(config["experiments"][-1], config)
        self.assertEqual(grid[0], {"max_depth": 2, "min_child_weight": 20, "learning_rate": .05})
        rows = dataset(1, 10)
        for row in rows:
            row["vector"][3:6] = [0, 0, math.hypot(105, 68)]
        result = explore(rows, config)
        self.assertTrue(all(v is None for row in result["pearson"] for v in row))
        self.assertEqual(result["distributions"]["nearest_visible_defender_distance_m"]["shots"], 0)

    def test_no_candidate_and_simpler_model_selection(self):
        rows=[{'match_id':i//2} for i in range(40)]
        y=np.array([0,1]*20);constant=np.full(40,.5);good=np.where(y,.8,.2)
        candidate={'id':'full_logistic','probabilities':constant}
        self.assertIsNone(select(rows,y,[candidate],constant,protocol())[0])
        candidate={'id':'geometry_logistic','probabilities':good}
        selected,_=select(rows,y,[candidate,{'id':'full_xgboost','probabilities':good}],constant,protocol())
        self.assertEqual(selected['id'],'geometry_logistic')
        self.assertFalse(choose_calibration(rows,y,good,good,protocol())[0])

    def test_finite_schema_export_and_fold_local_scaler(self):
        rows=dataset(10,10);config=protocol();experiment=config['experiments'][0]
        x,y=arrays(rows,experiment['indices'])
        model=fit(estimator(experiment,{'C':.1},config),x,y)
        provenance={'preparation_run_id':'a'*64,'feature_run_id':'b'*64,'source_revision':'invented',
                    'protocol_sha256':'c'*64,'split_sha256':'d'*64,'code_sha256':{},'dependencies':{}}
        artifact=export_estimator(model,experiment,provenance,config)
        self.assertLessEqual(verify_parity(artifact,model,np.asarray([r['vector'] for r in rows]),experiment['indices'],{'method':'identity'},1e-10),1e-10)
        changed=copy.deepcopy(artifact);changed['parameters']['scale'][0]=0
        with self.assertRaises(AuditError): validate_envelope(seal(changed))
        changed=copy.deepcopy(artifact);changed['feature_order'].reverse()
        with self.assertRaises(AuditError): validate_envelope(seal(changed))
        changed=copy.deepcopy(artifact);changed['real_rows']=[]
        with self.assertRaises(ValidationError): validate_envelope(seal(changed))
        with self.assertRaises(AuditError):predict_envelope(artifact,[[float('nan')]*8])
        folds={str(r['match_id']):r['match_id']%5 for r in rows}
        seen=[]
        original_fit=fit
        def observe(model,x,y):
            fitted=original_fit(model,x,y)
            seen.append((fitted.named_steps['scale'].mean_.copy(),np.mean(x,axis=0)))
            return fitted
        with patch('training.fit',side_effect=observe):tune(rows,folds,experiment,config)
        self.assertEqual(len(seen),21)
        for actual, expected in seen:np.testing.assert_allclose(actual,expected,atol=1e-12)


class CompleteWorkflowTests(unittest.TestCase):
    def test_complete_reproduction_test_label_isolation_and_failure_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);rows=dataset();write_features(root/'features',rows)
            prepared=prepare(root/'features',root/'prepared')
            split=read_json(prepared/'split.json')
            self.assertEqual(read_json(prepared/'preparation-summary.json')['test_status'],'unopened')
            first=train(prepared,root/'run-a')
            second=train(prepared,root/'run-b')
            self.assertEqual(compare_runs(first,second)['run_id'],first.name)
            self.assertEqual(compare_training(first,second)['byte_differences'],[])
            evaluation=read_json(first/'evaluation.json')
            self.assertEqual((first/'methodology.md').read_bytes(),render_report(evaluation))
            validate_evaluation(evaluation)
            self.assertEqual(len(evaluation['experiments']),5)
            self.assertEqual(evaluation['test_status'],'unopened')
            self.assertNotIn('goals',evaluation['partitions']['test'])
            for check in evaluation['export_checks'].values():self.assertLessEqual(check['absolute_probability_error'],check['tolerance'])
            mutated=root/'mutated';mutated.mkdir()
            for p in prepared.iterdir():(mutated/p.name).write_bytes(p.read_bytes())
            held=[json.loads(line) for line in (mutated/'test.jsonl').read_text().splitlines()]
            for r in held:r['is_goal']=1-r['is_goal']
            (mutated/'test.jsonl').write_text(''.join(canonical(r) for r in held))
            resign(mutated)
            third=train(mutated,root/'run-mutated')
            other=read_json(third/'evaluation.json')
            self.assertEqual(evaluation['training_exploration'],other['training_exploration'])
            self.assertEqual(evaluation['experiments'],other['experiments'])
            a,b=copy.deepcopy(evaluation['selection']),copy.deepcopy(other['selection'])
            a.pop('selected_artifact_id',None);b.pop('selected_artifact_id',None)
            self.assertEqual(a,b)
            self.assertEqual(read_json(first/'validation-predictions.json'),read_json(third/'validation-predictions.json'))
            changed=copy.deepcopy(evaluation);changed['partitions']['test']['goals']=1
            with self.assertRaises(ValidationError):validate_evaluation(changed)
            changed=copy.deepcopy(evaluation);changed['training_exploration']['vector']=[1]
            with self.assertRaises(ValidationError):validate_evaluation(changed)
            (mutated/'selection.jsonl').write_text('corrupted')
            with self.assertRaises(AuditError):train(mutated,root/'failure')
            self.assertFalse((root/'failure').exists())
            with self.assertRaises(AuditError):prepare(root/'features',root/'features'/'illegal')
            with self.assertRaises(AuditError):compare_training(first,first)
            with self.assertRaises(AuditError):compare_json({'shots':1},{'shots':2},1e-6)


if __name__=='__main__':unittest.main()
