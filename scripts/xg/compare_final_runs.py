#!/usr/bin/env python3
"""Verify complete final runs and compare scientific evidence and private predictions."""

import argparse
from pathlib import Path
import sys

import numpy as np
from jsonschema import ValidationError

from compare_runs import verified_run
from evaluation import checked, metrics
from ingest_statsbomb import AuditError
from report_final import verify_views
from run_io import read_json

INVENTORY={'manifest.json','final-evaluation.json','release-checks.json','app-evidence.json',
           'methodology.md','model-card.md','protocol.json','test-predictions.json'}


def verified_final(directory):
    root,manifest,names=verified_run(directory)
    if manifest.get('phase')!='final-evaluation' or names!=INVENTORY:
        raise AuditError('Expected complete final-evaluation phase/inventory; use the printed completed directory')
    e=verify_views(root)
    if any(manifest.get(k)!=v for k,v in e['provenance'].items()) or manifest.get('evidence_id')!=e['evidence_id'] or manifest.get('release_status')!=e['release_checks']['status']:
        raise AuditError('Final manifest and evidence provenance differ')
    predictions=read_json(root/'test-predictions.json')
    if set(predictions)!={'match_ids','labels','probabilities'} or set(predictions['probabilities'])!={'selected','full_logistic','constant'}:
        raise AuditError('Invalid private final prediction fields')
    n=e['test_summary']['shots']
    mids=predictions['match_ids'];y=predictions['labels']
    if (len(mids)!=n or len(y)!=n or any(type(mid) is not int or mid<=0 for mid in mids)
            or any(type(label) is not int or label not in (0,1) for label in y)
            or len(set(mids))!=e['test_summary']['matches'] or sum(y)!=e['test_summary']['goals']):
        raise AuditError('Private prediction identities/counts differ')
    for record in e['results']:
        p=predictions['probabilities'][record['role']]
        checked(y,p)
        scores=metrics(y,p,e['development_evidence']['protocol'])
        if any(abs(scores[k]-record['metrics'][k])>1e-12 for k in scores):
            raise AuditError('Private probabilities and aggregate scores differ')
    return root,manifest,names


def compare_value(a,b,tolerance,path='root'):
    if type(a)!=type(b):
        raise AuditError('Final reproduction type differs: '+path)
    if isinstance(a,dict):
        if a.keys()!=b.keys():raise AuditError('Final reproduction fields differ: '+path)
        for k in a:
            if k!='evidence_id':compare_value(a[k],b[k],tolerance,path+'.'+k)
    elif isinstance(a,list):
        if len(a)!=len(b):raise AuditError('Final reproduction length differs: '+path)
        for i,(x,y) in enumerate(zip(a,b)):compare_value(x,y,tolerance,f'{path}[{i}]')
    elif isinstance(a,float):
        if not np.isfinite(a) or not np.isfinite(b) or abs(a-b)>tolerance:
            raise AuditError('Final reproduction numeric tolerance failed: '+path)
    elif a!=b:
        raise AuditError('Final reproduction decision/count/value differs: '+path)


def compare_final(left_dir,right_dir):
    if Path(left_dir).resolve()==Path(right_dir).resolve():
        raise AuditError('Comparison requires distinct completed runs')
    left,lm,lf=verified_final(left_dir);right,rm,rf=verified_final(right_dir)
    if lf!=rf:raise AuditError('Final inventories differ')
    a=read_json(left/'final-evaluation.json');b=read_json(right/'final-evaluation.json')
    if a['provenance']!=b['provenance'] or a['protocol']!=b['protocol']:
        raise AuditError('Final scientific provenance/protocol differs')
    tolerance=a['protocol']['tolerances']
    byte_differences=[]
    for name in sorted(lf):
        if (left/name).read_bytes()!=(right/name).read_bytes():byte_differences.append(name)
        if name.endswith('.md') or name=='manifest.json':continue
        compare_value(read_json(left/name),read_json(right/name),
                      tolerance['probability'] if name=='test-predictions.json' else tolerance['metric'],name)
    if verified_run(left)[1]!=lm or verified_run(right)[1]!=rm:
        raise AuditError('Final run changed during comparison')
    return {'files_verified':len(lf),'byte_differences':byte_differences,
            'python_versions':[lm['python_version'],rm['python_version']]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--left-dir',type=Path,required=True);parser.add_argument('--right-dir',type=Path,required=True)
    args=parser.parse_args()
    try:result=compare_final(args.left_dir,args.right_dir)
    except (AuditError,OSError,ValueError,KeyError,TypeError,ValidationError) as exc:
        print('FAIL: '+(str(exc) if isinstance(exc,AuditError) else 'Invalid/incomplete final evaluation evidence'),file=sys.stderr)
        return 1
    print(f"PASS: {result['files_verified']} files verified; {len(result['byte_differences'])} files differ byte for byte")
    print('PASS: final scientific configuration, decisions, reports/app views and numeric tolerances agree')
    print('Python versions: '+', '.join(result['python_versions']))
    return 0


if __name__=='__main__':sys.exit(main())
