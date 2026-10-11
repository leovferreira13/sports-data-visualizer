"""Frozen historical-run compatibility, checked before any held-out parsing."""

from check_browser_inference import code_hashes, selected_candidate
from compare_runs import verified_run
from features import CONTRACT_PATH
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import validate_envelope
from prepare_training import PARTITIONS, matches, summary
from report_training import validate_evaluation
from run_io import PROJECT, load_json, protocol, read_json
from training import dependencies

CRITICAL = ('scripts/xg/features.py', 'scripts/xg/ingest_statsbomb.py', 'scripts/xg/extract_features.py',
            'scripts/xg/prepare_training.py', 'scripts/xg/train_models.py', 'scripts/xg/training.py',
            'scripts/xg/evaluation.py', 'scripts/xg/model_export.py', 'scripts/xg/scene_evaluation.py',
            'scripts/xg/requirements.lock', 'model/feature-contract.json', 'model/model-artifact.schema.json',
            'lib/presets.ts', 'tests/fixtures/training-presets.json')


def historical_compatibility(manifest):
    recorded = manifest.get('code_sha256', {})
    for path in CRITICAL:
        if recorded.get(path) != sha256((PROJECT/path).read_bytes()):
            raise AuditError('Historical scientific semantics differ: '+path)


def rows_in(directory, partition):
    return [load_json(line) for line in (directory/f'{partition}.jsonl').read_bytes().splitlines()]


def inputs(prepared_dir, training_dir, parity_dir):
    train_root, tm, selected = selected_candidate(training_dir)
    prepared, pm, names = verified_run(prepared_dir)
    parity_root, bm, bnames = verified_run(parity_dir)
    expected = {'manifest.json','protocol.json','split.json','preparation-summary.json',
                *(f'{p}.jsonl' for p in PARTITIONS)}
    if pm.get('phase') != 'preparation' or names != expected:
        raise AuditError('Expected complete preparation phase')
    if (tm.get('preparation_run_id') != pm['run_id'] or tm.get('feature_run_id') != pm['feature_run_id']
            or tm.get('source_revision') != pm['source']['source_revision']
            or tm.get('split_sha256') != sha256((prepared/'split.json').read_bytes())
            or (prepared/'split.json').read_bytes() != (train_root/'split.json').read_bytes()
            or read_json(prepared/'protocol.json') != protocol()
            or pm.get('protocol_sha256') != tm['protocol_sha256']
            or pm.get('feature_contract_sha256') != sha256(CONTRACT_PATH.read_bytes())):
        raise AuditError('Frozen preparation/training linkage differs')
    historical_compatibility(tm)
    historical_compatibility(pm)
    if tm['dependencies'] != dependencies():
        raise AuditError('Installed scientific dependency versions differ from frozen run')
    e = read_json(train_root/'evaluation.json')
    validate_evaluation(e)
    if e['provenance'] != selected['provenance'] or e['protocol'] != protocol():
        raise AuditError('Training evaluation provenance differs')
    if read_json(train_root/'selection.json') != e['selection']:
        raise AuditError('Training decision differs')
    logistic = read_json(train_root/'full_logistic.json')
    validate_envelope(logistic)
    if logistic['model_version'] != 'full_logistic' or logistic['provenance'] != selected['provenance']:
        raise AuditError('Required frozen full-logistic baseline differs')
    for envelope in (selected, logistic):
        experiment = next(x for x in e['experiments'] if x['id'] == envelope['model_version'])
        method = 'sigmoid' if experiment['calibration_decision']['adopted'] else 'identity'
        if envelope['calibration']['method'] != method:
            raise AuditError('Frozen calibration decision differs')
    if bm.get('phase') != 'browser-inference' or bnames != {'manifest.json','parity.json'}:
        raise AuditError('Expected complete actual-candidate browser parity phase')
    b = read_json(parity_root/'parity.json')
    if (bm.get('training_run_id') != tm['run_id'] or b.get('training_run_id') != tm['run_id']
            or b.get('status') != 'pass' or b.get('evidence_scope') != 'frozen-local-candidate'
            or bm.get('evidence_scope') != b['evidence_scope'] or b.get('held_out_labels_accessed') is not False
            or b.get('parameters_published') is not False or b.get('code_sha256') != code_hashes()
            or bm.get('code_sha256') != b['code_sha256'] or len(b.get('checks', [])) != 1):
        raise AuditError('Parity is not matching current frozen-candidate evidence; rerun parity without retraining')
    c = b['checks'][0]
    if (c.get('artifact_id') != selected['artifact_id'] or c.get('model_version') != selected['model_version']
            or c.get('status') != 'pass' or c.get('tolerance') != selected['export_tolerance']
            or not 0 <= c.get('max_probability_error', -1) <= c['tolerance']):
        raise AuditError('Selected artifact parity differs')
    split = read_json(prepared/'split.json')['partitions']
    if set(split.values()) != set(PARTITIONS):
        raise AuditError('Invalid frozen split')
    development = {p: rows_in(prepared,p) for p in PARTITIONS if p != 'test'}
    seen = set()
    reports = read_json(prepared/'preparation-summary.json')
    for part, rows in development.items():
        group = matches(rows)
        if ({str(mid) for mid in group} != {mid for mid, p in split.items() if p == part}
                or seen.intersection(group) or summary(rows) != e['partitions'][part]
                or reports['partitions'][part] != e['partitions'][part]):
            raise AuditError('Development membership or counts differ')
        seen.update(group)
    if reports['test_status'] != 'unopened' or reports['partitions']['test'] != e['partitions']['test']:
        raise AuditError('Historical test summary differs')
    constant = read_json(train_root/'constant-reference.json')
    prevalence = sum(r['is_goal'] for r in development['train'])/len(development['train'])
    if constant != {'probability': prevalence, 'fitted_partition': 'train'}:
        raise AuditError('Constant reference differs from frozen training prevalence')
    return {'prepared':prepared,'training':train_root,'parity':parity_root,'pm':pm,'tm':tm,'bm':bm,
            'selected':selected,'logistic':logistic,'constant':prevalence,'development':e,
            'training_rows':development['train'],'split':split,'development_matches':seen}


def test_rows(context):
    rows = rows_in(context['prepared'],'test')
    grouped = matches(rows)
    split = context['split']
    if ({str(mid) for mid in grouped} != {mid for mid,p in split.items() if p == 'test'}
            or context['development_matches'].intersection(grouped)
            or summary(rows, False) != context['development']['partitions']['test']):
        raise AuditError('Held-out membership/isolation or label-blind counts differ')
    return rows
