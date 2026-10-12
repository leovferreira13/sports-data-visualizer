#!/usr/bin/env python3
"""Reserve whole unused matches before fitting, then open once for a frozen choice."""

import argparse
import os
from pathlib import Path
import sys

import numpy as np
from jsonschema import ValidationError

from behavior_io import original_inputs, research_codes, research_protocol, recheck_inputs
from behavior_statistics import quality
from compare_behavior_runs import verified_research
from compare_runs import verified_run
from features import CONTRACT_PATH
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import predict_envelope
from prepare_training import matches, summary
from run_io import PROJECT, load_json, output_root, publish, read_json
from training import arrays

RESERVATION_FILES = {'manifest.json', 'protocol.json', 'membership.json', 'usage-declaration.json', 'reserved-rows.jsonl'}


def usage_declaration(declaration, original_membership):
    expected = {'prior_use_complete', 'outcomes_not_used_for_choice', 'prior_match_ids', 'eligibility'}
    if (not isinstance(declaration, dict) or set(declaration) != expected
            or declaration['prior_use_complete'] is not True
            or declaration['outcomes_not_used_for_choice'] is not True
            or not isinstance(declaration['eligibility'], str) or not declaration['eligibility'].strip()
            or not isinstance(declaration['prior_match_ids'], list)
            or any(type(mid) is not int or mid <= 0 for mid in declaration['prior_match_ids'])):
        raise AuditError('A complete private prior-use ledger and outcome-use declaration are required')
    known = set(declaration['prior_match_ids'])
    if not {int(mid) for mid in original_membership} <= known:
        raise AuditError('Prior-use ledger omits original train/calibration/selection/test matches')
    return known


def reserve(prepared_dir, training_dir, feature_dir, declaration_path, output_dir):
    config, codes = research_protocol(), research_codes()
    context = original_inputs(prepared_dir, training_dir, config)
    source, fm, names = verified_run(feature_dir)
    if (names != {'manifest.json', 'features.jsonl', 'feature-audit.json'}
            or fm.get('contract_version') != 'positional-features/v1'
            or fm.get('code_sha256', {}).get('model/feature-contract.json') != sha256(CONTRACT_PATH.read_bytes())
            or not isinstance(fm.get('ingestion', {}).get('source_revision'), str)):
        raise AuditError('Expected a pinned complete fresh feature run')
    for path in ('scripts/xg/features.py', 'scripts/xg/ingest_statsbomb.py', 'scripts/xg/extract_features.py'):
        if fm.get('code_sha256', {}).get(path) != codes[path]:
            raise AuditError('Fresh feature semantics differ')
    declaration = read_json(declaration_path)
    declaration_bytes = Path(declaration_path).read_bytes()
    known = usage_declaration(declaration, context['split']['partitions'])
    # JSON decoding sees bytes containing labels; reservation only examines identities,
    # never outcome values, feature distributions, support counts or candidate performance.
    data = (source/'features.jsonl').read_bytes()
    identities = {}
    shots = 0
    for line in data.splitlines():
        row = load_json(line)
        mid, cid, sid = (row.get(k) for k in ('match_id', 'competition_id', 'season_id'))
        if any(type(v) is not int or v <= 0 for v in (mid, cid, sid)):
            raise AuditError('Invalid reservation membership')
        if mid in known:
            raise AuditError('Fresh reservation overlaps previously used matches')
        if mid in identities and identities[mid] != (cid, sid):
            raise AuditError('Conflicting fresh match metadata')
        identities[mid] = (cid, sid)
        shots += 1
    if not identities:
        raise AuditError('Fresh reservation contains no eligible matches')
    membership = {'matches': {str(mid): list(value) for mid, value in sorted(identities.items())},
                  'shots': shots, 'label_values_examined': False,
                  'prior_use_verification': 'local ledger plus explicit declaration; unknown external use not mechanically proven'}
    files = {'protocol.json': config, 'membership.json': membership, 'usage-declaration.json': declaration,
             'reserved-rows.jsonl': data}
    provenance = {'protocol_sha256': sha256(canonical(config).encode()), 'code_sha256': codes,
                  'original_training_run_id': context['tm']['run_id'], 'original_preparation_run_id': context['pm']['run_id'],
                  'fresh_feature_run_id': fm['run_id'], 'fresh_source_revision': fm['ingestion']['source_revision'],
                  'reserved_rows_sha256': sha256(data), 'feature_contract_sha256': sha256(CONTRACT_PATH.read_bytes())}
    def guard():
        recheck_inputs(context, codes)
        if verified_run(source)[1] != fm or Path(declaration_path).read_bytes() != declaration_bytes:
            raise AuditError('Reservation inputs changed')
    return publish(output_dir, source, 'behavior-holdout-reservation', files, provenance, guard)


def reservation_for_research(directory, context, config, codes):
    root, manifest, names = verified_run(directory)
    if (manifest.get('phase') != 'behavior-holdout-reservation' or names != RESERVATION_FILES
            or manifest.get('code_sha256') != codes or read_json(root/'protocol.json') != config
            or manifest.get('original_training_run_id') != context['tm']['run_id']
            or manifest.get('original_preparation_run_id') != context['pm']['run_id']
            or manifest.get('protocol_sha256') != sha256(canonical(config).encode())
            or manifest.get('reserved_rows_sha256') != sha256((root/'reserved-rows.jsonl').read_bytes())):
        raise AuditError('Reservation must match the protocol/code and precede this research fitting')
    known = usage_declaration(read_json(root/'usage-declaration.json'), context['split']['partitions'])
    membership = read_json(root/'membership.json')['matches']
    if not membership or {int(mid) for mid in membership}.intersection(known):
        raise AuditError('Reserved matches overlap prior use')
    return manifest


def evaluate_fresh(research_dir, reservation_dir, output_dir):
    root, rm, e = verified_research(research_dir)
    reserved, sm, names = verified_run(reservation_dir)
    config = e['protocol']
    chosen = e['selection']['recommended_model']
    if chosen is None:
        raise AuditError('No frozen alternative qualifies; fresh outcomes remain unopened')
    if (names != RESERVATION_FILES or sm.get('phase') != 'behavior-holdout-reservation'
            or e['reservation_run_id'] != sm['run_id'] or rm.get('reservation_run_id') != sm['run_id']
            or sm.get('code_sha256') != research_codes() or sm.get('code_sha256') != rm['code_sha256']
            or read_json(reserved/'protocol.json') != config
            or sm.get('original_training_run_id') != e['original_training_run_id']):
        raise AuditError('Fresh reservation is not bound before fitting to this frozen research run')
    output = output_root(output_dir, reserved)
    # Access is recorded before loading labels, and survives evaluation failure. Copies
    # cannot provide a software security guarantee; this is an explicit local procedure.
    access = reserved.parent/'.behavior-test-access'
    access.mkdir(exist_ok=True)
    marker = access/('opened-'+sm['run_id']+'.json')
    try:
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise AuditError('Fresh outcomes were already opened; do not retune or describe a retry as untouched') from exc
    with os.fdopen(fd, 'w') as handle:
        handle.write(canonical({'reservation_run_id': sm['run_id'], 'research_run_id': rm['run_id'],
                                'candidate_artifact_id': e['models'][chosen]['artifact_id'], 'status': 'opened'}))
    rows = [load_json(line) for line in (reserved/'reserved-rows.jsonl').read_bytes().splitlines()]
    grouped = matches(rows)
    membership = read_json(reserved/'membership.json')
    if ({str(mid): [values[0]['competition_id'], values[0]['season_id']] for mid, values in grouped.items()}
            != membership['matches'] or len(rows) != membership['shots']):
        raise AuditError('Fresh membership differs; access remains recorded')
    x, y = arrays(rows, list(range(8)))
    path = 'logistic-model.json' if chosen == 'full_logistic' else 'candidate-model.json'
    candidate = read_json(root/path)
    current = read_json(root/'current-model.json')
    # The original training prevalence is frozen in aggregate research evidence.
    constant = np.full(len(y), e['training_prevalence'])
    final_config = read_json(PROJECT/'model/final-evaluation-protocol.json')
    scores = quality(rows, y, predict_envelope(candidate, x), constant, predict_envelope(current, x),
                     config['original_training_protocol'], final_config, config)
    info = summary(rows)
    minima, limits = config['fresh_minima'], config['decision']
    checks = {'support': info['matches'] >= minima['matches'] and info['goals'] >= minima['goals']
                        and info['shots']-info['goals'] >= minima['non_goals'],
              **{k: scores['paired_with_current'][k]['upper_95'] is not None
                 and scores['paired_with_current'][k]['upper_95'] <= limits['max_'+k+'_degradation']
                 for k in ('log_loss', 'brier')}, 'constant_reference': scores['beats_constant']}
    reviews = [f'calibration_bin:{i}' for i, r in enumerate(scores['calibration_bins']) if r['review_flag']]
    reviews += [f'slice:{i}' for i, r in enumerate(scores['slices']) if r['review_flag']]
    result = {'schema_version': 1, 'evaluation_scope': 'reserved-unused-matches-subject-to-prior-use-declaration',
              'test_status': 'opened_once', 'research_run_id': rm['run_id'], 'reservation_run_id': sm['run_id'],
              'artifact_id': candidate['artifact_id'], 'selected_model': chosen, 'summary': info, 'quality': scores,
              'checks': checks, 'required_reviews': reviews,
              'status': 'needs_review' if all(checks.values()) else 'withheld', 'publication_authorized': False,
              'limitations': ['Prior-use completeness includes a user declaration; unknown external use cannot be proven.',
                              'No refit, calibration adjustment or reselection after opening. Local access marker is procedural.']}
    result['evidence_id'] = sha256(canonical(result).encode())
    def guard():
        if verified_run(root)[1] != rm or verified_run(reserved)[1] != sm or research_codes() != rm['code_sha256']:
            raise AuditError('Frozen research/reservation/code changed after test opening')
    return publish(output, reserved, 'behavior-fresh-evaluation', {'fresh-evaluation.json': result},
                   {'research_run_id': rm['run_id'], 'reservation_run_id': sm['run_id'],
                    'code_sha256': rm['code_sha256'], 'protocol_sha256': rm['protocol_sha256']}, guard)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    seal = commands.add_parser('reserve')
    for name in ('prepared-dir', 'training-dir', 'feature-dir', 'usage-declaration', 'output-dir'):
        seal.add_argument('--'+name, type=Path, required=True)
    test = commands.add_parser('evaluate')
    for name in ('research-dir', 'reservation-dir', 'output-dir'):
        test.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    try:
        root = (reserve(args.prepared_dir, args.training_dir, args.feature_dir, args.usage_declaration, args.output_dir)
                if args.command == 'reserve' else evaluate_fresh(args.research_dir, args.reservation_dir, args.output_dir))
    except (AuditError, OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
        message = str(exc) if isinstance(exc, AuditError) else 'Invalid holdout input or output boundary'
        print('FAIL: '+message+'. Inspect access records before describing test access.', file=sys.stderr)
        return 1
    print(f'Complete immutable {args.command} run: {root}; publication remains unauthorized')
    return 0


if __name__ == '__main__':
    sys.exit(main())
