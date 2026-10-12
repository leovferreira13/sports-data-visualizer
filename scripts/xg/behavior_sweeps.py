"""Predeclared isolated probes and physical paths, with private per-step traces."""

import copy
import math

import numpy as np

from features import extract_metric_features, FEATURE_NAMES
from final_scenes import support_reference
from ingest_statsbomb import AuditError
from model_export import predict_envelope
from run_io import PROJECT, read_json
from scene_evaluation import scenes

FIXTURES = PROJECT / 'tests/fixtures/behavior-scenes.json'


def grid(spec):
    values = np.arange(spec['min'], spec['max'], spec['step']).tolist()
    if not values or values[-1] != spec['max']:
        values.append(spec['max'])
    return np.asarray(values)


def anchors(training_rows, config):
    result = [(s['name'], extract_metric_features(s['scene'])['vector'])
              for s in scenes()[:6] if s['scene']['shot_type'] == 'open-play']
    # Selection is independent of outcomes; exact private anchor values stay local.
    if training_rows:
        rng = np.random.default_rng(config['sweeps']['anchor_seed'])
        take = np.sort(rng.choice(len(training_rows), min(len(training_rows),
                           config['sweeps']['training_anchors']), replace=False))
        result += [(f'training_anchor_{i}', training_rows[int(n)]['vector']) for i, n in enumerate(take)]
    return result


def isolated_cases(training_rows, config):
    result = []
    for name, anchor in anchors(training_rows, config):
        for index, direction in ((0, -1), (1, 1)):
            values = grid(config['sweeps'][FEATURE_NAMES[index]])
            vectors = np.tile(anchor, (len(values), 1)).astype(float)
            vectors[:, index] = values
            result.append({'name': name + ':' + FEATURE_NAMES[index], 'index': index,
                           'direction': direction, 'axis': values, 'vectors': vectors})
    return result


def direction_summary(probabilities, direction, tolerance):
    delta = np.diff(np.asarray(probabilities)) * direction
    bad = delta < -tolerance
    return {'pairs': len(delta), 'violations': int(bad.sum()),
            'violation_rate': float(bad.mean()) if len(delta) else 0.,
            'max_violation': float(-delta[bad].min()) if bad.any() else 0.}


def response_summary(probabilities, axis, tolerance, jump, mask=None):
    p, axis = np.asarray(probabilities), np.asarray(axis)
    delta = np.abs(np.diff(p))
    take = np.ones(len(delta), dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    if take.shape != delta.shape:
        raise AuditError('Invalid sweep segment mask')
    d = delta[take]
    longest = running = 0.
    for flat, width in zip((delta <= tolerance) & take, np.diff(axis)):
        running = running + float(width) if flat else 0.
        longest = max(longest, running)
    return {'pairs': int(take.sum()), 'plateau_share': float((d <= tolerance).mean()) if len(d) else None,
            'longest_plateau_span': longest, 'median_jump': float(np.median(d)) if len(d) else None,
            'p95_jump': float(np.quantile(d, .95)) if len(d) else None,
            'max_jump': float(d.max()) if len(d) else None,
            'large_jump_rate': float((d > jump).mean()) if len(d) else None}


def physical_cases(config):
    fixture = read_json(FIXTURES)
    base = copy.deepcopy(scenes()[0]['scene'])
    result = []

    def append(name, points, actor, index, context):
        records, axis, coordinates = [], [0.], []
        for point in points:
            scene = copy.deepcopy(base)
            if index is None:
                scene[actor] = {'x': float(point[0]), 'y': float(point[1])}
            else:
                scene[actor][index] = {'x': float(point[0]), 'y': float(point[1])}
            f = extract_metric_features(scene)
            if f['status'] != 'ok':
                raise AuditError('Declared physical path contains unsupported scene')
            if coordinates:
                axis.append(axis[-1] + math.dist(coordinates[-1], point))
            coordinates.append(point)
            records.append({'scene': scene, 'vector': f['vector']})
        result.append({'name': name, 'context': context, 'axis': np.asarray(axis),
                       'records': records, 'vectors': np.asarray([r['vector'] for r in records])})

    for path in fixture['paths']:
        start, end = np.asarray(path['start']), np.asarray(path['end'])
        count = math.ceil(float(np.linalg.norm(end-start)) / config['sweeps']['physical_step_m'])
        append(path['name'], np.linspace(start, end, count+1).tolist(),
               path['actor'], path['index'], path['context'])
    arc = fixture['arc']
    start, end = math.radians(arc['angle_start_deg']), math.radians(arc['angle_end_deg'])
    count = math.ceil((end-start)*arc['radius_m']/config['sweeps']['physical_step_m'])
    points = [[105-arc['radius_m']*math.cos(a), 34+arc['radius_m']*math.sin(a)]
              for a in np.linspace(start, end, count+1)]
    append(arc['name'], points, 'shooter', None, 'ordinary')
    return result


def boundary_cases():
    fixture = read_json(FIXTURES)['cone_probe']
    base = copy.deepcopy(scenes()[0]['scene'])
    base['shooter'] = dict(zip(('x', 'y'), fixture['shooter']))
    x = fixture['defender_x']
    y = 34 + 3.66 * (x-base['shooter']['x']) / (105-base['shooter']['x'])
    cases = []
    for label, offset in (('inside', -fixture['epsilon_m']), ('on', 0), ('outside', fixture['epsilon_m'])):
        scene = copy.deepcopy(base)
        scene['defenders'] = [{'x': x, 'y': y+offset}]
        cases.append({'name': 'cone_' + label, 'scene': scene})
    for count in range(4):
        scene = copy.deepcopy(base)
        scene['defenders'] = [{'x': 96+i, 'y': 34+i} for i in range(count)]
        cases.append({'name': f'defender_count_{count}', 'scene': scene})
    return cases


def support_flags(vectors, refs):
    flags = []
    for v in vectors:
        ref, _ = refs[v[3] == 0]
        if ref is None:
            flags.append('insufficient_reference')
            continue
        indices, mean, scale, keep, tree, threshold, _ = ref
        z = (v[indices][keep]-mean[keep])/scale[keep]
        flags.append('within_training_reference' if float(tree.query(z)[0]/np.sqrt(z.size)) <= threshold
                     else 'outside_training_reference')
    return flags


def evaluate_sweeps(envelope, training_rows, config, support_config, predictor=None):
    predict = predictor or (lambda vectors: predict_envelope(envelope, vectors, validate=False))
    tolerance, jump = config['sweeps']['tolerance'], config['sweeps']['large_jump']
    isolated, physical, details = [], [], {}
    for case in isolated_cases(training_rows, config):
        p = predict(case['vectors'])
        isolated.append({'name': case['name'], 'axis_unit': 'm' if case['index'] == 0 else 'degrees',
                         **direction_summary(p, case['direction'], tolerance),
                         **response_summary(p, case['axis'], tolerance, jump)})
        details[case['name']] = {'axis': case['axis'].tolist(), 'probabilities': np.asarray(p).tolist(),
                                'vectors': case['vectors'].tolist(), 'physical_consistency': 'not_required'}
    refs = {zero: support_reference(training_rows, list(range(8)), zero, support_config) for zero in (False, True)}
    pools = {name: [] for name in ('primary', 'outside_reference', 'extreme', 'count_transition')}
    for case in physical_cases(config):
        p = np.asarray(predict(case['vectors']))
        delta_features = np.diff(case['vectors'], axis=0)
        continuous = np.all(delta_features[:, 3:5] == 0, axis=1)
        flags = support_flags(case['vectors'], refs)
        supported = np.asarray([a == b == 'within_training_reference' for a, b in zip(flags, flags[1:])])
        ordinary = case['context'] == 'ordinary'
        masks = {'primary': continuous & supported & ordinary,
                 'outside_reference': continuous & ~supported & ordinary,
                 'extreme': continuous & (not ordinary), 'count_transition': ~continuous}
        summaries = {}
        jumps = np.abs(np.diff(p))
        for category, mask in masks.items():
            summaries[category] = response_summary(p, case['axis'], tolerance, jump, mask)
            pools[category].extend(jumps[mask].tolist())
        physical.append({'name': case['name'], 'context': case['context'], 'points': len(p),
                         'feature_changes': [name for i, name in enumerate(FEATURE_NAMES)
                                             if np.any(delta_features[:, i] != 0)],
                         'reversals_are_partial_violations': False, 'segments': summaries})
        details[case['name']] = {'axis_m': case['axis'].tolist(), 'probabilities': p.tolist(),
                                'records': case['records'], 'feature_deltas': delta_features.tolist(),
                                'support_categories': flags}
    pooled = {name: {'pairs': len(values), 'p95_jump': float(np.quantile(values, .95)) if values else None,
                     'large_jump_rate': float(np.mean(np.asarray(values) > jump)) if values else None,
                     'max_jump': max(values) if values else None} for name, values in pools.items()}
    boundaries = []
    for case in boundary_cases():
        f = extract_metric_features(case['scene'])
        p = float(predict([f['vector']])[0])
        boundaries.append({'name': case['name'], 'probability': p,
                           'defender_count': f['vector'][3], 'cone_count': f['vector'][4]})
    return {'isolated': isolated, 'physical': physical, 'pooled': pooled, 'boundaries': boundaries,
            'partial_direction_pass': all(r['violations'] == 0 for r in isolated),
            'support_note': 'Training-only nearest-neighbor diagnostic; no proof of calibration or realism. '
                            'Primary segments have two within-reference endpoints and unchanged count features.'}, details
