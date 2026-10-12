"""Exploratory scores and explicit quality/interaction gates, never publication."""

import numpy as np

from evaluation import bins, losses, metrics, paired_difference, slice_masks
from final_statistics import interval, match_weights
from training import improvement


def quality(rows, y, probabilities, constant, current, training_config, final_config, config):
    group, draws = match_weights(rows, final_config)
    mask = np.ones(len(rows), dtype=bool)
    candidate_losses = losses(y, probabilities, training_config['metric_clip'])
    current_losses = losses(y, current, training_config['metric_clip'])
    paired = {}
    # A central 90% percentile interval's upper endpoint is the one-sided 95% bound.
    confidence = 2*config['decision']['one_sided_confidence']-1
    for key in candidate_losses:
        result = interval(candidate_losses[key]-current_losses[key], mask, group, draws, confidence)
        paired[key] = {'difference': result['estimate'], 'upper_95': result['interval'][1]
                       if result['interval'] is not None else None}
    constant_comparison = paired_difference(rows, y, probabilities, constant, training_config)
    calibration = []
    assignments = np.minimum((np.asarray(probabilities)*10).astype(int), 9)
    for i, record in enumerate(bins(y, probabilities, training_config)):
        take = assignments == i
        residual = interval(np.asarray(y)-probabilities, take, group, draws, .95) if take.any() else None
        ci = residual['interval'] if residual else None
        calibration.append({**record, 'residual_interval': residual,
                            'review_flag': bool(not record['sparse'] and ci is not None and (ci[0] > 0 or ci[1] < 0))})
    masks = list(slice_masks(rows, training_config))
    x = np.asarray([r['vector'] for r in rows])
    for count in range(11):
        masks.append(('defenders_in_cone_count', {'value': count}, x[:, 4] == count))
    slices = []
    for name, boundary, take in masks:
        n, g = int(take.sum()), int(np.asarray(y)[take].sum())
        sparse = n < final_config['sparse']['shots'] or g < final_config['sparse']['goals']
        paired_slice = {key: interval(candidate_losses[key]-current_losses[key], take, group, draws, .95)
                        for key in candidate_losses} if n else None
        ci = paired_slice['log_loss']['interval'] if n else None
        slices.append({'feature': name, **boundary, 'shots': n, 'goals': g, 'sparse': sparse,
                       'metrics': metrics(np.asarray(y)[take], np.asarray(probabilities)[take], training_config) if n else None,
                       'paired_with_current': paired_slice,
                       'review_flag': bool(not sparse and ci is not None and ci[0] > 0)})
    return {'metrics': metrics(y, probabilities, training_config), 'paired_with_current': paired,
            'paired_with_constant': constant_comparison,
            'beats_constant': improvement(constant_comparison, training_config),
            'calibration_bins': calibration, 'slices': slices}


def gates(record, current_behavior, config):
    q, b = record['quality'], record['behavior']
    limits = config['decision']
    probability_gates = {key: q['paired_with_current'][key]['upper_95'] is not None
                         and q['paired_with_current'][key]['upper_95'] <= limits['max_'+key+'_degradation']
                         for key in ('log_loss', 'brier')}
    a, ref = b['pooled']['primary'], current_behavior['pooled']['primary']
    available = a['pairs'] > 0 and a['pairs'] == ref['pairs']
    jump_pass = False
    if available:
        if ref['large_jump_rate'] == 0:
            jump_pass = a['large_jump_rate'] == 0 and a['p95_jump'] < ref['p95_jump']
        else:
            jump_pass = (a['large_jump_rate'] <= ref['large_jump_rate']*(1-limits['min_jump_rate_reduction'])
                         and a['p95_jump'] <= ref['p95_jump'])
    predicates = {**probability_gates, 'constant_reference': q['beats_constant'],
                  'partial_directions': b['partial_direction_pass'], 'primary_segments_available': available,
                  'interactive_improvement': bool(jump_pass), 'invariants': record['scene_audit']['invariants_pass'],
                  'parity': record['parity']['status'] == 'pass', 'native_export': record['native_export_pass']}
    reviews = [f'calibration_bin:{i}' for i, value in enumerate(q['calibration_bins']) if value['review_flag']]
    reviews += [f'slice:{i}' for i, value in enumerate(q['slices']) if value['review_flag']]
    return {'predicates': predicates, 'eligible': all(predicates.values()), 'required_reviews': reviews,
            'failures': [k for k, v in predicates.items() if not v]}


def select_candidates(records, config):
    checks = {name: record['gates'] for name, record in records.items() if name != 'full_xgboost'}
    chosen = next((name for name in config['decision']['order'] if name in checks and checks[name]['eligible']), None)
    return {'status': 'recommend_pending_independent_evaluation' if chosen else 'retain_current',
            'recommended_model': chosen, 'candidate_checks': checks,
            'publication_authorized': False, 'fresh_test_status': 'not_available',
            'rationale': 'Predeclared quality bounds, partial directions and supported-path jump gates; '
                         'logistic wins when both alternatives qualify. Adaptive selection is exploratory.'}
