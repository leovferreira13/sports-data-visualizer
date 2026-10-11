"""Final-test probability summaries with paired whole-match bootstrap draws."""

import numpy as np

from evaluation import bins, checked, losses, metrics, slice_masks
from features import FEATURE_NAMES


def match_weights(rows, config):
    mids = sorted({r['match_id'] for r in rows})
    lookup = {mid: i for i, mid in enumerate(mids)}
    group = np.array([lookup[r['match_id']] for r in rows])
    rng = np.random.default_rng(config['bootstrap']['seed'])
    draws = np.array([np.bincount(rng.integers(0, len(mids), len(mids)), minlength=len(mids))
                      for _ in range(config['bootstrap']['resamples'])])
    return group, draws


def interval(values, mask, group, draws, confidence):
    values = np.asarray(values, dtype=float)
    counts = np.bincount(group[mask], minlength=draws.shape[1])
    sums = np.bincount(group[mask], weights=values[mask], minlength=draws.shape[1])
    den = draws @ counts
    valid = den > 0
    estimates = (draws[valid] @ sums) / den[valid]
    alpha = (1 - confidence) / 2
    # One represented match cannot establish between-match uncertainty.
    supported = np.count_nonzero(counts) >= 2 and len(estimates) >= 2
    return {'estimate': float(values[mask].mean()),
            'interval': np.quantile(estimates, [alpha, 1-alpha]).tolist() if supported else None,
            'valid_resamples': int(valid.sum()), 'skipped_resamples': int((~valid).sum())}


def summarize(rows, y, probabilities, training_config, config):
    y = np.asarray(y)
    group, draws = match_weights(rows, config)
    confidence = config['bootstrap']['confidence']
    values = {k: {**losses(y, p, training_config['metric_clip']), 'prevalence': y,
                  'mean_probability': np.asarray(p)} for k, p in probabilities.items()}

    def uncertainty(role, mask):
        return {k: interval(v, mask, group, draws, confidence) for k, v in values[role].items()}

    def paired(a, b, mask):
        return {k: interval(values[a][k]-values[b][k], mask, group, draws, confidence)
                for k in ('log_loss', 'brier')}

    masks = list(slice_masks(rows, training_config))
    x = np.asarray([r['vector'] for r in rows])
    for name, edges in config['additional_bins'].items():
        v = x[:, FEATURE_NAMES.index(name)]
        for i, (lo, hi) in enumerate(zip(edges, edges[1:])):
            take = (v >= lo) & ((v <= hi if i == len(edges)-2 else v < hi) if hi is not None else True)
            if name == 'nearest_visible_defender_distance_m':
                take &= x[:, 3] != 0
            masks.append((name, {'lower': lo, 'upper': hi}, take))
    masks.append(('nearest_visible_defender_distance_m', {'value': 0}, x[:, 3] == 0))
    all_rows = np.ones(len(rows), dtype=bool)
    output = {}
    for role, p in probabilities.items():
        checked(y, p)
        calibration = []
        assignments = np.minimum((np.asarray(p)*10).astype(int), 9)
        for i, record in enumerate(bins(y, p, training_config)):
            take = assignments == i
            record = {**record, 'matches': len(set(group[take].tolist())),
                      'observed_interval': interval(y, take, group, draws, confidence) if take.any() else None,
                      'residual_interval': interval(y-np.asarray(p), take, group, draws, confidence) if take.any() else None}
            ci = record['residual_interval']['interval'] if record['residual_interval'] else None
            record['review_flag'] = bool(not record['sparse'] and ci is not None and (ci[0] > 0 or ci[1] < 0))
            calibration.append(record)
        slices = []
        for name, boundary, take in masks:
            n, g = int(take.sum()), int(y[take].sum())
            slices.append({'feature': name, **{k: boundary.get(k) for k in ('lower','upper','value','competition_id','season_id')},
                           'shots': n, 'goals': g, 'matches': len(set(group[take].tolist())),
                           'sparse': n < config['sparse']['shots'] or g < config['sparse']['goals'],
                           'metrics': metrics(y[take], np.asarray(p)[take], training_config) if n else None,
                           'uncertainty': uncertainty(role, take) if n else None,
                           'paired': {b: paired(role, b, take) for b in ('constant','full_logistic')} if n else None})
        output[role] = {'metrics': metrics(y, p, training_config), 'uncertainty': uncertainty(role, all_rows),
                        'calibration_bins': calibration, 'slices': slices}
    return output, {f'selected_minus_{b}': paired('selected', b, all_rows) for b in ('constant','full_logistic')}
