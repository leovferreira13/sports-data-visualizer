#!/usr/bin/env python3
"""Evaluate the frozen candidate once; deterministic reruns reproduce an opened test."""

import argparse
from pathlib import Path
import sys

import numpy as np
from jsonschema import ValidationError
from threadpoolctl import threadpool_limits

from check_browser_inference import code_hashes
from compare_runs import verified_run
from final_inputs import inputs, test_rows
from final_release import release_checks
from final_scenes import audit_scenes
from final_statistics import summarize
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import predict_envelope
from prepare_training import summary
from run_io import PROJECT, code_identity, output_root, publish, read_json

PROTOCOL_PATH = PROJECT/'model/final-evaluation-protocol.json'


def opening_record(context, config, output):
    # Lives outside completed runs; survives exceptions after test access begins.
    # Also put a deterministic record beside the immutable preparation, so a new
    # output root cannot misleadingly imply the same test is still untouched.
    value = {'test_status':'opened-for-final-evaluation', 'training_run_id':context['tm']['run_id'],
             'preparation_run_id':context['pm']['run_id'],
             'final_protocol_sha256':sha256(canonical(config).encode()),
             'meaning':'Opening intent recorded before parsing outcomes; a failed/interrupted attempt may already have exposed them. Repeats are reproduction, not untouched evaluation.'}
    destinations = (output, context['prepared'].parent/'.final-test-access')
    for root in destinations:
        if any(p.is_symlink() for p in (root,*root.parents)):
            raise AuditError('Test-access record cannot contain links')
        root.mkdir(parents=True,exist_ok=True)
        path = root/f"test-opened-{context['tm']['run_id']}-{value['final_protocol_sha256']}.json"
        try:
            with path.open('x',encoding='utf-8') as stream:
                stream.write(canonical(value))
        except FileExistsError:
            if path.is_symlink() or read_json(path) != value:
                raise AuditError('Existing test-access record differs')
    return value


def evaluate(prepared_dir, training_dir, parity_dir, output_dir):
    context = inputs(prepared_dir, training_dir, parity_dir)
    config = read_json(PROTOCOL_PATH)
    # Check the reviewed protocol before recording/opening; changing thresholds
    # requires a distinct explicit evaluation policy, never a silent retry.
    from report_final import validate_protocol, public_outputs
    validate_protocol(config)
    output = output_root(output_dir, context['prepared'])
    for root in (context['training'],context['parity']):
        output_root(output_dir,root)
    codes = {**code_identity(), **code_hashes()}
    opening_record(context,config,output)
    rows = test_rows(context)
    y = np.asarray([r['is_goal'] for r in rows])
    vectors = np.asarray([r['vector'] for r in rows])
    selected, logistic = context['selected'], context['logistic']
    probabilities = {'selected':predict_envelope(selected,vectors),
                     'full_logistic':predict_envelope(logistic,vectors),
                     'constant':np.full(len(rows),context['constant'])}
    with threadpool_limits(limits=1):
        results, paired = summarize(rows,y,probabilities,context['development']['protocol'],config)
        scene = audit_scenes(selected,context['training_rows'],config)
    for role, model in (('selected',selected),('full_logistic',logistic),('constant',None)):
        results[role].update(role=role, model_version=model['model_version'] if model else 'constant-training-prevalence',
                             artifact_id=model['artifact_id'] if model else None)
    provenance = {
        'training_run_id':context['tm']['run_id'],'preparation_run_id':context['pm']['run_id'],
        'parity_run_id':context['bm']['run_id'],'feature_run_id':context['tm']['feature_run_id'],
        'source_revision':context['tm']['source_revision'],
        'selected_artifact_id':selected['artifact_id'],'logistic_artifact_id':logistic['artifact_id'],
        'split_sha256':context['tm']['split_sha256'],'feature_contract_sha256':context['tm']['feature_contract_sha256'],
        'training_protocol_sha256':context['tm']['protocol_sha256'],
        'final_protocol_sha256':sha256(canonical(config).encode()), 'code_sha256':codes,
        'dependencies':context['tm']['dependencies'],
        'historical_compatibility':'recorded manifests validated; unchanged scientific semantics checked separately',
        **{f'{label}_manifest_sha256':sha256((context[key]/'manifest.json').read_bytes())
           for label,key in (('training','training'),('preparation','prepared'),('parity','parity'))}}
    e = {'schema_version':1,'contract_version':config['version'],'provenance':provenance,'protocol':config,
         'test_status':'opened-final-evaluation','test_summary':summary(rows),
         'population':context['development']['population'],'results':[results[k] for k in config['models']],
         'paired':paired,'scene_audit':scene,'development_evidence':context['development'],
         'limitations':[
             'Match-isolated holdout measures the represented cohort, not unseen league/period transfer.',
             'Defender observations are partial embedded shot frames; optional 360 coverage is not a test-row covariate.',
             'Missing/multiple keepers are excluded; no valid prediction is obtained by imputing a keeper.',
             'Zero observed defenders do not establish an empty pitch; sentinel support can be absent or extremely sparse.',
             'Support distances are training-only diagnostics, not proof of realistic joint player configurations.',
             'Full-pitch training scenes differ from current marker-safe UI bounds; historical UI audit is descriptive.',
             'Extra attackers, technique, identity, preceding movement and unobserved pressure are omitted.',
             'Controlled responses are within-model comparisons; tree plateaus and nonmonotonic changes can be valid.',
             'Slice/calibration intervals are diagnostic, sparse bins remain uncertain and multiple comparisons are not confirmatory.',
             'Penalties, headers and non-open-play shots are excluded; penalty 0.76 is a separate fixed convention.',
             'StatsBomb supplies Open Data, not this independent model; non-commercial rights/export review and actual-product QA remain required.'
         ]}
    e['release_checks'] = release_checks(e)
    e['evidence_id'] = sha256(canonical(e).encode())
    files = public_outputs(e)
    files.update({'protocol.json':config, 'test-predictions.json':{
        'match_ids':[r['match_id'] for r in rows], 'labels':y.tolist(),
        'probabilities':{k:v.tolist() for k,v in probabilities.items()}}})

    def guard():
        if {**code_identity(),**code_hashes()} != codes:
            raise AuditError('Scientific code changed during final evaluation')
        for key,mkey in (('prepared','pm'),('training','tm'),('parity','bm')):
            if verified_run(context[key])[1] != context[mkey]:
                raise AuditError('Frozen input changed during final evaluation')

    return publish(output,context['prepared'],'final-evaluation',files,
                   {**provenance,'evidence_id':e['evidence_id'],'release_status':e['release_checks']['status']},guard)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared-dir','training-dir','parity-dir','output-dir'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    try:
        destination=evaluate(args.prepared_dir,args.training_dir,args.parity_dir,args.output_dir)
    except (AuditError,OSError,ValueError,KeyError,TypeError,ValidationError) as exc:
        message=str(exc) if isinstance(exc,AuditError) else 'Invalid inputs, contract, dependency or output boundary'
        print(f'FAIL: {message}; no completed final run. Check the test-opened record before describing test access.',file=sys.stderr)
        return 1
    e=read_json(destination/'final-evaluation.json')
    print(f"Complete immutable final-evaluation run: {destination}")
    print(f"Evaluation status: {e['release_checks']['status']}; test opened; public xG remains disabled")
    if e['release_checks']['status']=='withheld':
        print('Withheld predicates: '+', '.join(k for k,v in e['release_checks']['predicates'].items() if not v))
        return 2
    return 0


if __name__=='__main__':
    sys.exit(main())
