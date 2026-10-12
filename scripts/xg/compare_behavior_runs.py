#!/usr/bin/env python3
"""Verify complete research inventories, regenerated views and numeric reproduction."""

import argparse
from pathlib import Path
import sys

from jsonschema import ValidationError

from compare_runs import verified_run
from compare_training_runs import compare_json
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import validate_envelope
from report_behavior import render_report, validate_behavior
from run_io import read_json

EXPECTED = {'manifest.json', 'behavior-evaluation.json', 'selection.json', 'protocol.json', 'comparison.md',
            'parity.json', 'candidate-model.json', 'candidate-raw.json', 'current-model.json',
            'logistic-model.json', 'sweep-details.json', 'validation-predictions.json'}


def verified_research(directory):
    root, manifest, names = verified_run(directory)
    if manifest.get('phase') != 'behavior-research' or names != EXPECTED:
        raise AuditError('Expected a complete behavior-research run and exact inventory')
    e = read_json(root/'behavior-evaluation.json')
    validate_behavior(e)
    views = {
        'selection': read_json(root/'selection.json') == e['selection'],
        'protocol': read_json(root/'protocol.json') == e['protocol'],
        'report': (root/'comparison.md').read_bytes() == render_report(e),
        'parity': read_json(root/'parity.json') == {n: r['parity'] for n, r in e['models'].items()},
        'evidence_identity': manifest.get('evidence_id') == e['evidence_id'],
        'original_training': manifest.get('original_training_run_id') == e['original_training_run_id'],
        'reservation': manifest.get('reservation_run_id') == e['reservation_run_id'],
    }
    for name, agrees in views.items():
        if not agrees:
            raise AuditError('Research evidence/view differs: '+name)
    for key, value in e['provenance'].items():
        if manifest.get(key) != value:
            raise AuditError('Research manifest provenance differs')
    if manifest['protocol_sha256'] != sha256(canonical(e['protocol']).encode()):
        raise AuditError('Research protocol digest differs')
    for name, role in (('candidate-model.json','full_monotonic_xgboost'), ('current-model.json','full_xgboost'),
                       ('logistic-model.json','full_logistic'), ('candidate-raw.json', None)):
        envelope = read_json(root/name)
        validate_envelope(envelope)
        if role is not None:
            check = e['models'][role]['parity']
            if (envelope['artifact_id'] != e['models'][role]['artifact_id']
                    or envelope['model_version'] != role or check['artifact_id'] != envelope['artifact_id']
                    or check['status'] != 'pass' or check['tolerance'] != envelope['export_tolerance']
                    or not 0 <= check['max_probability_error'] <= envelope['export_tolerance']):
                raise AuditError('Research model/parity evidence differs')
    return root, manifest, e


def compare_behavior(left_dir, right_dir):
    if Path(left_dir).resolve() == Path(right_dir).resolve():
        raise AuditError('Comparison requires two distinct research runs')
    left, lm, le = verified_research(left_dir)
    right, rm, _ = verified_research(right_dir)
    for key in ('code_sha256', 'dependencies', 'protocol_sha256', 'preparation_run_id', 'feature_run_id',
                'source_revision', 'split_sha256', 'feature_contract_sha256', 'original_training_run_id', 'reservation_run_id'):
        if lm[key] != rm[key]:
            raise AuditError('Research provenance differs: '+key)
    differences = []
    tolerances = le['protocol']['original_training_protocol']['tolerances']
    for name in sorted(EXPECTED - {'manifest.json', 'comparison.md'}):
        if (left/name).read_bytes() != (right/name).read_bytes():
            differences.append(name)
        tolerance = tolerances['reproduction_probability'] if name in ('sweep-details.json', 'validation-predictions.json') else tolerances['reproduction_metric']
        compare_json(read_json(left/name), read_json(right/name), tolerance, name)
    if (left/'comparison.md').read_bytes() != (right/'comparison.md').read_bytes():
        differences.append('comparison.md')
    if verified_run(left)[1] != lm or verified_run(right)[1] != rm:
        raise AuditError('Research inputs changed during comparison')
    return {'files_verified': len(EXPECTED), 'byte_differences': differences,
            'python_versions': [lm['python_version'], rm['python_version']]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('left-dir', 'right-dir'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        result = compare_behavior(args.left_dir, args.right_dir)
    except (AuditError, OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
        print('FAIL: '+(str(exc) if isinstance(exc, AuditError) else 'Invalid complete research run'), file=sys.stderr)
        return 1
    print(f"PASS: {result['files_verified']} files verified; {len(result['byte_differences'])} files differ byte for byte")
    print('PASS: research provenance, decisions, topology and numeric tolerances agree')
    return 0


if __name__ == '__main__':
    sys.exit(main())
