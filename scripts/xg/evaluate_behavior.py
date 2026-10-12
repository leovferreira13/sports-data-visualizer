#!/usr/bin/env python3
"""Compare immutable references with a bounded monotonic candidate, offline only."""

import argparse
import copy
from pathlib import Path
import sys

import numpy as np
from jsonschema import ValidationError

from behavior_io import original_inputs, research_codes, research_protocol, recheck_inputs
from behavior_statistics import gates, quality, select_candidates
from behavior_sweeps import boundary_cases, evaluate_sweeps, isolated_cases, physical_cases, direction_summary
from check_browser_inference import verify
from compare_runs import verified_run
from evaluation import explore
from features import FEATURE_NAMES
from final_scenes import audit_scenes
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import IDENTITY, calibration_apply, export_estimator, predict_envelope, seal, validate_envelope
from report_behavior import evidence_identity, render_report
from run_io import PROJECT, publish, read_json
from train_models import verify_parity
from training import arrays, choose_calibration, dependencies, fit_calibration, predict, tune


def parity_cases(training_rows, config):
    result = []
    for case in isolated_cases(training_rows, config):
        for i, vector in enumerate(case['vectors']):
            result.append({'name': f"sweep:{case['name']}:{i}", 'mode': 'vector', 'value': vector.tolist()})
    for case in physical_cases(config):
        for i, record in enumerate(case['records']):
            result.append({'name': f"path:{case['name']}:{i}", 'mode': 'metric', 'value': record['scene']})
    result.extend({'name': case['name'], 'mode': 'metric', 'value': case['scene']} for case in boundary_cases())
    return result


def fit_candidate(context, config, provenance):
    original, experiment = config['original_training_protocol'], config['candidate']
    rows, folds = context['rows'], context['split']['train_folds']
    model, cv = tune(rows['train'], folds, experiment, original)
    if model is None:
        raise AuditError('Bounded monotonic fitting failed; no complete candidate evidence')
    selection_x, y = arrays(rows['selection'], list(range(8)))
    xc, yc = arrays(rows['calibration'], list(range(8)))
    raw_p = predict(model, selection_x)
    fitted = fit_calibration(yc, predict(model, xc), original)
    use, comparison = choose_calibration(rows['selection'], y, raw_p,
                                         calibration_apply(raw_p, fitted) if fitted else None, original)
    calibration = fitted if use else copy.deepcopy(IDENTITY)
    raw = export_estimator(model, experiment, provenance, original)
    envelope = copy.deepcopy(raw)
    envelope['calibration'] = calibration
    envelope = seal(envelope)
    validate_envelope(envelope)
    return model, raw, envelope, {'cv': cv, 'calibration': {'adopted': use, 'fit_status': 'ok' if fitted else 'declined',
                                                         'comparison': comparison}}


def evaluate(prepared_dir, training_dir, output_dir, browser=False, reservation_dir=None):
    config, codes = research_protocol(), research_codes()
    context = original_inputs(prepared_dir, training_dir, config)
    original = config['original_training_protocol']
    final_config = read_json(PROJECT/'model/final-evaluation-protocol.json')
    protocol_hash = sha256(canonical(config).encode())
    reservation_id = None
    if reservation_dir is not None:
        from behavior_holdout import reservation_for_research
        reservation_id = reservation_for_research(reservation_dir, context, config, codes)['run_id']
    provenance = {'preparation_run_id': context['pm']['run_id'], 'feature_run_id': context['pm']['feature_run_id'],
                  'source_revision': context['tm']['source_revision'], 'split_sha256': context['tm']['split_sha256'],
                  'protocol_sha256': protocol_hash, 'code_sha256': codes, 'dependencies': dependencies()}
    rows = context['rows']
    # Baseline diagnostics are generated before any new fitting.
    behaviors, details = {}, {}
    for name, envelope in (('full_xgboost', context['current']), ('full_logistic', context['logistic'])):
        print(f'Diagnosing frozen {name}', flush=True)
        behaviors[name], details[name] = evaluate_sweeps(envelope, rows['train'], config, final_config)
    print('Fitting bounded train-only monotonic candidate', flush=True)
    model, raw, candidate, training_record = fit_candidate(context, config, provenance)
    name = 'full_monotonic_xgboost'
    behaviors[name], details[name] = evaluate_sweeps(candidate, rows['train'], config, final_config)
    native_directions = {}
    for stage, predictor in (('native_raw', lambda x: predict(model, np.asarray(x))),
                             ('native_calibrated', lambda x: calibration_apply(predict(model, np.asarray(x)), candidate['calibration'])),
                             ('exported_raw', lambda x: predict_envelope(raw, x, validate=False))):
        records = [direction_summary(predictor(case['vectors']), case['direction'], config['sweeps']['tolerance'])
                   for case in isolated_cases(rows['train'], config)]
        native_directions[stage] = {'pairs': sum(r['pairs'] for r in records),
                                    'violations': sum(r['violations'] for r in records),
                                    'max_violation': max(r['max_violation'] for r in records)}
    all_x, y = arrays(rows['selection'], list(range(8)))
    all_cases = parity_cases(rows['train'], config)
    # Add every valid tree boundary from the existing parity harness for native/export checking.
    from check_browser_inference import cases_for
    from check_browser_inference import reference
    boundary_vectors = [c['value'] for c in cases_for(candidate) if c['mode'] == 'vector'
                        and reference(c, candidate)['probability'] is not None]
    probe_vectors = np.vstack([all_x, arrays(rows['calibration'], list(range(8)))[0],
                              *[c['vectors'] for c in isolated_cases(rows['train'], config)],
                              *[c['vectors'] for c in physical_cases(config)], boundary_vectors])
    export_errors = {stage: verify_parity(envelope, model, probe_vectors, list(range(8)),
                                         envelope['calibration'], 1e-7)
                     for stage, envelope in (('raw', raw), ('calibrated', candidate))}
    envelopes = {'full_xgboost': context['current'], 'full_logistic': context['logistic'], name: candidate}
    probabilities = {n: predict_envelope(e, all_x) for n, e in envelopes.items()}
    constant = np.full(len(y), context['constant'])
    records = {}
    for n, envelope in envelopes.items():
        print(f'Checking quality and browser parity: {n}', flush=True)
        records[n] = {'artifact_id': envelope['artifact_id'], 'quality': quality(rows['selection'], y, probabilities[n],
                      constant, probabilities['full_xgboost'], original, final_config, config),
                      'behavior': behaviors[n], 'scene_audit': audit_scenes(envelope, rows['train'], final_config),
                      'parity': verify(envelope, browser, all_cases), 'native_export_pass': True}
        if n == name:
            records[n]['native_export_pass'] = all(r['violations'] == 0 for r in native_directions.values())
    for n, record in records.items():
        if n != 'full_xgboost':
            record['gates'] = gates(record, behaviors['full_xgboost'], config)
    params = context['logistic']['parameters']
    exploration = explore(rows['train'], original)
    evaluation = {'schema_version': 1, 'contract_version': 'xg-behavior-evaluation/v1',
                  'feature_order': list(FEATURE_NAMES), 'protocol': config, 'provenance': provenance,
                  'evaluation_scope': 'adaptive-selection-exploratory', 'previous_final_test': 'already_opened_not_parsed',
                  'original_training_run_id': context['tm']['run_id'], 'reservation_run_id': reservation_id,
                  'models': records, 'training_prevalence': context['constant'], 'candidate_training': training_record,
                  'native_export': {'baseline_errors': context['baseline_native_errors'], 'errors': export_errors, 'directions': native_directions, 'vectors_checked': len(probe_vectors)},
                  'logistic_diagnostics': {'coefficients': dict(zip(FEATURE_NAMES, params['coefficients'])),
                       'scale': params['scale'], 'calibration': context['logistic']['calibration'],
                       'correlation_feature_order': list(FEATURE_NAMES), 'train_only_pearson': exploration['pearson'],
                       'train_only_spearman': exploration['spearman'], 'sentinel_rows_excluded': True},
                  'selection': select_candidates(records, config),
                  'limitations': ['Selection data and prior final findings informed this follow-up; exploratory evidence only.',
                       'Tree constraints do not imply smoothness or monotonicity on every physical drag.',
                       'Joint support diagnostics and synthetic paths do not establish empirical calibration.',
                       'Rounded reported distance/angle examples lack full coordinates; fixtures are analogues.',
                       'No goalkeeper defaults, published artifact or localized methodology values are changed.']}
    evaluation['evidence_id'] = evidence_identity(evaluation)
    files = {'behavior-evaluation.json': evaluation, 'selection.json': evaluation['selection'], 'protocol.json': config,
             'comparison.md': render_report(evaluation), 'parity.json': {n: r['parity'] for n, r in records.items()},
             'candidate-model.json': candidate, 'candidate-raw.json': raw, 'current-model.json': context['current'],
             'logistic-model.json': context['logistic'], 'sweep-details.json': details,
             'validation-predictions.json': {'match_ids': [r['match_id'] for r in rows['selection']], 'labels': y.tolist(),
                                           'probabilities': {n: p.tolist() for n, p in probabilities.items()}}}
    return publish(output_dir, context['prepared'], 'behavior-research', files,
                   {**provenance, 'original_training_run_id': context['tm']['run_id'], 'reservation_run_id': reservation_id,
                    'evidence_id': evaluation['evidence_id'], 'feature_contract_sha256': candidate['feature_contract_sha256']},
                   lambda: recheck_inputs(context, codes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('prepared-dir', 'training-dir', 'output-dir'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--reservation-dir', type=Path)
    parser.add_argument('--browser', action='store_true', help='Also execute the bundle in actual Chromium')
    args = parser.parse_args()
    try:
        root = evaluate(args.prepared_dir, args.training_dir, args.output_dir, args.browser, args.reservation_dir)
    except (AuditError, OSError, ValueError, TypeError, KeyError, ValidationError) as exc:
        message = str(exc) if isinstance(exc, AuditError) else 'Invalid research inputs, dependency, schema or output boundary'
        print('FAIL: '+message+'; no completed research run', file=sys.stderr)
        return 1
    print(f'Complete immutable research run: {root}')
    print('Disposition: '+read_json(root/'selection.json')['status']+'; exploratory; published model unchanged')
    return 0


if __name__ == '__main__':
    sys.exit(main())
