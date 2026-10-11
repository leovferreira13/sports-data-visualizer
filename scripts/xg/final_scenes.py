"""Synthetic response and training-only feature-space support diagnostics."""

import numpy as np
from scipy.spatial import cKDTree

from features import extract_metric_features
from model_export import predict_envelope
from scene_evaluation import scenes


def support_reference(rows, indices, zero, config):
    # The sentinel is categorical missingness, not a continuous distance.
    if zero:
        indices = [i for i in indices if i != 5]
    train = np.asarray([r['vector'] for r in rows if (r['vector'][3] == 0) == zero])
    if len(train) < 2:
        return None, len(train)
    train = train[:, indices]
    mean, scale = train.mean(axis=0), train.std(axis=0)
    keep = scale > 0
    if not keep.any():
        return None, len(train)
    z = (train[:, keep]-mean[keep])/scale[keep]
    rng = np.random.default_rng(config['support']['seed'])
    choose = np.sort(rng.choice(len(z), min(len(z), config['support']['reference_max_rows']), replace=False))
    reference = z[choose]
    tree = cKDTree(reference)
    nearest = tree.query(reference, k=2)[0][:, 1] / np.sqrt(reference.shape[1])
    threshold = float(np.quantile(nearest, config['support']['quantile']))
    return (indices, mean, scale, keep, tree, threshold, len(reference)), len(train)


def audit_scenes(envelope, training_rows, config):
    indices = envelope['feature_indices']
    refs = {zero: support_reference(training_rows, indices, zero, config) for zero in (False, True)}
    low = np.asarray([r['vector'] for r in training_rows]).min(axis=0)
    high = np.asarray([r['vector'] for r in training_rows]).max(axis=0)
    records = []
    for fixture in scenes():
        f = extract_metric_features(fixture['scene'])
        record = {'scene': fixture['name'], 'status': 'unsupported', 'reason': f.get('reason'),
                  'probability': None, 'outside_training_marginals': None, 'support_category': 'unsupported',
                  'support_distance': None, 'support_threshold': None, 'support_reference_rows': 0,
                  'support_cohort_rows': 0, 'zero_defender_support_unestablished': False}
        if f.get('reason') == 'penalty_separate_route':
            record.update(status='penalty-convention', reason=None, probability=.76, support_category='convention')
        elif f['status'] == 'ok':
            v = np.asarray(f['vector'])
            zero = v[3] == 0
            ref, count = refs[zero]
            record.update(status='ok', reason=None, probability=float(predict_envelope(envelope, [v])[0]),
                          outside_training_marginals=bool(((v < low) | (v > high)).any()),
                          support_category='insufficient_reference', support_cohort_rows=count,
                          zero_defender_support_unestablished=bool(zero))
            if ref is not None:
                ix, mean, scale, keep, tree, threshold, n = ref
                z = (v[ix][keep]-mean[keep])/scale[keep]
                distance = float(tree.query(z)[0]/np.sqrt(z.size))
                record.update(support_distance=distance, support_threshold=threshold, support_reference_rows=n,
                              support_category='outside_training_reference' if distance > threshold else 'within_training_reference')
        records.append(record)
    lookup = {r['scene']: r for r in records}
    base = lookup['centralChance']['probability']
    tolerance = envelope['export_tolerance']
    differences = {group: [lookup[n]['probability']-base for n in names] for group, names in {
        'keeper': ('keeper_advanced','keeper_lateral','keeper_extreme'),
        'defender': ('zero_defenders','one_defender','added_defender','cone_inside','cone_outside','nearest_defender')}.items()}
    responses = {group: bool(any(abs(d) > tolerance for d in differences[group])) if index in indices else True
                 for group, index in (('keeper',6),('defender',3))}
    invariants = all(abs(lookup[n]['probability']-base) <= tolerance for n in ('reflection','reordered_defenders'))
    invariants &= lookup['missing_keeper']['status'] == 'unsupported' and lookup['goal_line']['status'] == 'unsupported'
    for group, index in (('keeper',6),('defender',3)):
        if index not in indices:
            invariants &= all(abs(d) <= tolerance for d in differences[group])
    return {'diagnostics': records, 'responses': responses, 'invariants_pass': bool(invariants),
            'probability_differences': differences,
            'support_method': 'Training-only standardized retained-feature RMS nearest neighbor; deterministic reference subsample, 99th-percentile leave-one-out threshold. Zero-defender cohort separate; sentinel distance omitted. This diagnostic is not proof of realistic joint scene support or a runtime rejection rule.'}
