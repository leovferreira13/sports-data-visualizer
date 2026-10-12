"""Check the actual integrated envelope against independent Python on invented scenes.

No private training directory is required; this supplements, rather than replaces,
the original frozen-training parity evidence. --browser needs separate Playwright.
"""
import argparse
import copy
import hashlib
import json
import random
import subprocess
from pathlib import Path

import numpy as np
from features import extract_metric_features
from model_export import predict_envelope

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    raw = (ROOT / 'model/selected-model.json').read_bytes()
    envelope = json.loads(raw)
    rights = json.loads((ROOT / 'docs/reports/xg-artifact-distribution-review.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == rights['file_sha256']
    assert envelope['artifact_id'] == rights['artifact_id']
    cases, expected = [], []
    fixtures = json.loads((ROOT / 'tests/fixtures/training-presets.json').read_text())

    def add(scene, removed=(), extra=()):
        scene = copy.deepcopy(scene)
        defenders = scene['defenders']
        scenario = {'shotType': scene['shot_type'], 'players': {'shooter': scene['shooter'],
                    'goalkeeper': scene['goalkeepers'][0], 'defender1': defenders[0], 'defender2': defenders[1]},
                    'extraAttackers': [], 'extraDefenders': list(extra), 'removedBaseDefenders': list(removed)}
        scene['defenders'] = [p for i, p in enumerate(defenders) if f'defender{i+1}' not in removed] + list(extra)
        scene['observation'] = 'browser-scene'
        f = extract_metric_features(scene)
        p = .76 if scene['shot_type'] == 'penalty' else None
        cases.append({'mode': 'scenario', 'value': scenario})
        expected.append({'probability': p, 'features': f})

    for fixture in fixtures:
        add(fixture['scene'])
    rng = random.Random(4)
    for i in range(200):
        scene = copy.deepcopy(fixtures[0]['scene'])
        for point in [scene['shooter'], *scene['goalkeepers'], *scene['defenders']]:
            point.update(x=rng.uniform(53.9, 103.6), y=rng.uniform(1.4, 66.6))
        removed = ('defender1', 'defender2') if i % 4 == 0 else ('defender1',) if i % 4 == 1 else ()
        extra = ({'x': rng.uniform(53.9, 103.6), 'y': rng.uniform(1.4, 66.6)},) if i % 4 == 3 else ()
        add(scene, removed, extra)
    # Valid float32 threshold vectors. Count thresholds use only integer neighbors.
    base = [21., 20., 0., 2., 1., 5., 3., 18.]
    seen = set()
    for nodes in envelope['parameters']['trees']:
        for node in nodes:
            if 'leaf' in node:
                continue
            feature, threshold = node['feature'], node['threshold']
            for v in (np.nextafter(np.float32(threshold), np.float32(-np.inf)), np.float32(threshold),
                      np.nextafter(np.float32(threshold), np.float32(np.inf))):
                row = base.copy()
                row[feature] = float(v)
                if feature in (3, 4):
                    row[feature] = float(round(row[feature]))
                    if feature == 3:
                        row[4] = min(row[4], row[3])
                    else:
                        row[3] = max(row[3], row[4])
                    if row[3] == 0:
                        continue
                key = tuple(row)
                if key in seen or any(x < 0 for x in row):
                    continue
                seen.add(key)
                cases.append({'mode': 'vector', 'value': row})
                expected.append({'probability': None, 'vector': row})
    active = [(i, e.get('vector', e.get('features', {}).get('vector'))) for i, e in enumerate(expected) if e['probability'] is None]
    for (i, _), probability in zip(active, predict_envelope(envelope, [v for _, v in active])):
        expected[i]['probability'] = float(probability)
    output = subprocess.run(['node', str(ROOT / 'scripts/xg/integrated_inference_runner.mjs'),
                             *(['--browser'] if args.browser else [])], cwd=ROOT,
                            input=json.dumps({'cases': cases, 'envelope': envelope}), text=True, capture_output=True, check=True)
    result = json.loads(output.stdout)
    assert result['artifact_id'] == envelope['artifact_id']
    assert len(result['cases']) == len(expected)
    maximum_probability_error, maximum_feature_error = 0., 0.
    for case, target in zip(result['cases'], expected):
        probability = case.get('probability', case.get('result', {}).get('probability'))
        assert probability is not None
        error = abs(probability - target['probability'])
        maximum_probability_error = max(maximum_probability_error, error)
        assert error <= 1e-7
        if 'features' in target and target['features']['status'] == 'ok':
            actual, vector = case['features']['vector'], target['features']['vector']
            for a, b in zip(actual, vector):
                maximum_feature_error = max(maximum_feature_error, abs(a-b))
                assert abs(a-b) <= 1e-9 + 1e-9 * abs(b)
    report = {'schema_version': 1, 'scope': 'invented scenes and float32 threshold vectors; actual integrated artifact',
              'artifact_id': envelope['artifact_id'], 'file_sha256': rights['file_sha256'],
              'cases': len(cases), 'engine': result['engine'], 'bundle_bytes': result['bundle_bytes'],
              'maximum_probability_error': maximum_probability_error, 'maximum_feature_error': maximum_feature_error,
              'probability_tolerance': 1e-7, 'status': 'PASS'}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
