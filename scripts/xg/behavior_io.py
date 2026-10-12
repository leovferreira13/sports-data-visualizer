"""A separate research boundary; historical inference/final guards stay strict."""

import numpy as np

from jsonschema import validate

from compare_runs import verified_run
from features import CONTRACT_PATH, FEATURE_NAMES
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import predict_envelope, validate_envelope
from prepare_training import PARTITIONS, fold_assignments, matches, require_classes, summary
from report_training import validate_evaluation
from run_io import PROJECT, code_identity, load_json, read_json
from training import dependencies

PROTOCOL = PROJECT / 'model/behavior-protocol.json'
PUBLISHED = PROJECT / 'model/selected-model.json'
REVIEWED_TRAINING = PROJECT / 'docs/reports/xg-training-first-run/manifest.json'


def research_protocol():
    config = read_json(PROTOCOL)
    validate(config, read_json(PROJECT / 'model/behavior-protocol.schema.json'))
    if config['feature_order'] != list(FEATURE_NAMES):
        raise AuditError('Research feature order drift')
    return config


def research_codes():
    codes = code_identity()
    for path in ('tests/fixtures/behavior-scenes.json', 'lib/model.ts', 'lib/features.ts',
                 'lib/predict.ts', 'lib/scenario.ts', 'lib/geometry.ts', 'package-lock.json',
                 'scripts/xg/inference_bridge.ts', 'scripts/xg/browser_inference_runner.mjs'):
        codes[path] = sha256((PROJECT / path).read_bytes())
    return codes


def original_inputs(prepared_dir, training_dir, config):
    prepared, pm, pn = verified_run(prepared_dir)
    training, tm, tn = verified_run(training_dir)
    required = {'manifest.json', 'protocol.json', 'split.json', 'preparation-summary.json',
                *(f'{p}.jsonl' for p in PARTITIONS)}
    if pm.get('phase') != 'preparation' or pn != required or tm.get('phase') != 'training':
        raise AuditError('Expected complete original preparation and training phases')
    if tm != read_json(REVIEWED_TRAINING):
        raise AuditError('Original training manifest is not the exact reviewed reference')
    needed = {'validation-predictions.json', 'full_logistic.json', 'selected-model.json', 'selection.json', 'evaluation.json',
              'split.json', 'protocol.json', 'constant-reference.json'}
    if not needed <= tn:
        raise AuditError('Missing original reference evidence')
    original = config['original_training_protocol']
    protocol_hash = sha256(canonical(original).encode())
    if any(read_json(root/'protocol.json') != original for root in (prepared, training)):
        raise AuditError('Original protocol differs from the pinned research reference')
    if (tm.get('preparation_run_id') != pm['run_id'] or tm.get('feature_run_id') != pm['feature_run_id']
            or tm.get('protocol_sha256') != protocol_hash or pm.get('protocol_sha256') != protocol_hash
            or tm.get('source_revision') != pm['source']['source_revision']
            or tm.get('split_sha256') != sha256((prepared/'split.json').read_bytes())
            or (prepared/'split.json').read_bytes() != (training/'split.json').read_bytes()
            or pm.get('feature_contract_sha256') != sha256(CONTRACT_PATH.read_bytes())):
        raise AuditError('Original preparation/training linkage differs')
    # Old training/export semantics travel with the immutable baseline. Current feature
    # semantics must still match; research fitting has its own complete code identity.
    for path in ('scripts/xg/features.py', 'scripts/xg/extract_features.py',
                 'scripts/xg/ingest_statsbomb.py', 'model/feature-contract.json'):
        current = sha256((PROJECT/path).read_bytes())
        if any(m.get('code_sha256', {}).get(path) != current for m in (pm, tm)):
            raise AuditError('Original feature semantics differ: ' + path)
    selected, logistic = (read_json(training/n) for n in ('selected-model.json', 'full_logistic.json'))
    for envelope, kind in ((selected, 'full_xgboost'), (logistic, 'full_logistic')):
        validate_envelope(envelope)
        if envelope['model_version'] != kind:
            raise AuditError('Original baseline kind differs')
        for key, value in envelope['provenance'].items():
            if tm.get(key) != value:
                raise AuditError('Original envelope provenance differs')
        if (training/(kind+'.json')).read_bytes() != canonical(envelope).encode():
            raise AuditError('Original envelope experiment bytes differ')
    if selected != read_json(PUBLISHED):
        raise AuditError('Original selected envelope is not the exact published model')
    e = read_json(training/'evaluation.json')
    validate_evaluation(e)
    if (e['provenance'] != selected['provenance'] or e['protocol'] != original
            or e['selection'] != read_json(training/'selection.json')
            or e['selection'].get('selected_artifact_id') != selected['artifact_id']
            or e['selection'].get('selected_model') != 'full_xgboost'
            or e['selection'].get('status') != 'frozen_candidate'):
        raise AuditError('Original decision/evaluation differs')
    for envelope in (selected, logistic):
        record = next(r for r in e['experiments'] if r['id'] == envelope['model_version'])
        adopted = record['calibration_decision']['adopted']
        if envelope['calibration']['method'] != ('sigmoid' if adopted else 'identity'):
            raise AuditError('Original calibration decision differs')
    split = read_json(prepared/'split.json')
    if set(split['partitions'].values()) != set(PARTITIONS):
        raise AuditError('Original partition names differ')
    # Verify test bytes through the manifest only. Never parse its rows or outcomes.
    rows = {p: [load_json(line) for line in (prepared/f'{p}.jsonl').read_bytes().splitlines()]
            for p in PARTITIONS if p != 'test'}
    seen = set()
    reports = read_json(prepared/'preparation-summary.json')
    for part, values in rows.items():
        group = matches(values)
        expected = {mid for mid, p in split['partitions'].items() if p == part}
        if (expected != {str(mid) for mid in group} or seen.intersection(group)
                or summary(values) != reports['partitions'][part]
                or reports['partitions'][part] != e['partitions'][part]):
            raise AuditError('Original development membership/counts differ')
        seen.update(group)
    folds = {str(k): v for k, v in fold_assignments(rows['train'], original).items()}
    if split['train_folds'] != folds:
        raise AuditError('Original fold assignment differs')
    for part in ('calibration', 'selection'):
        require_classes(rows[part], original['minima']['validation_class'])
    for fold in range(original['folds']):
        for held in (True, False):
            require_classes([r for r in rows['train'] if (folds[str(r['match_id'])] == fold) == held],
                            original['minima']['fold_class'])
    if (reports['test_status'] != 'unopened' or e['test_status'] != 'unopened'
            or reports['partitions']['test'] != e['partitions']['test']
            or 'goals' in reports['partitions']['test']):
        raise AuditError('Historical test metadata differs; previously opened status is recorded separately')
    prevalence = sum(r['is_goal'] for r in rows['train']) / len(rows['train'])
    if read_json(training/'constant-reference.json') != {'probability': prevalence, 'fitted_partition': 'train'}:
        raise AuditError('Original constant reference differs')
    if selected['provenance']['dependencies'] != dependencies():
        raise AuditError('Scientific dependencies differ from the original locked environment')
    native = read_json(training/'validation-predictions.json')
    selection_rows = rows['selection']
    if (native['match_ids'] != [r['match_id'] for r in selection_rows]
            or native['labels'] != [r['is_goal'] for r in selection_rows]):
        raise AuditError('Historical native reference membership/labels differ')
    baseline_errors = {}
    vectors = np.asarray([r['vector'] for r in selection_rows])
    for envelope in (selected, logistic):
        name = envelope['model_version']
        stored = e['export_checks'][name]
        if (stored['tolerance'] != envelope['export_tolerance']
                or not 0 <= stored['absolute_probability_error'] <= envelope['export_tolerance']
                or stored['vectors_checked'] <= 0):
            raise AuditError('Historical native/export evidence failed')
        expected = np.asarray(native['probabilities'][name+':'+envelope['calibration']['method']], dtype=float)
        actual = predict_envelope(envelope, vectors)
        if expected.shape != actual.shape or not np.isfinite(expected).all():
            raise AuditError('Historical native reference shape/numeric content differs')
        error = float(np.max(np.abs(actual-expected)))
        if error > envelope['export_tolerance']:
            raise AuditError('Frozen reference differs from original native predictions')
        baseline_errors[name] = error
    return {'baseline_native_errors': baseline_errors, 'prepared': prepared, 'training': training, 'pm': pm, 'tm': tm, 'rows': rows,
            'split': split, 'current': selected, 'logistic': logistic, 'constant': prevalence}


def recheck_inputs(context, codes):
    for root, manifest in ((context['prepared'], context['pm']), (context['training'], context['tm'])):
        if verified_run(root)[1] != manifest:
            raise AuditError('Original inputs changed during research')
    if research_codes() != codes:
        raise AuditError('Research configuration/code changed during evaluation')
