#!/usr/bin/env python3
"""Strict aggregate evidence validation and deterministic documentation/app views."""

import argparse
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

from final_release import release_checks
from ingest_statsbomb import AuditError, canonical, sha256
from report_training import validate_evaluation
from run_io import PROJECT, read_json

BASE='https://sports-data-visualizer.local/model/'


def schema_validate(value,name):
    names=('evaluation.schema.json','final-evaluation.schema.json','app-evidence.schema.json')
    documents={n:read_json(PROJECT/'model'/n) for n in names}
    registry=Registry().with_resources([(BASE+n,Resource.from_contents(doc)) for n,doc in documents.items()])
    Draft202012Validator(documents[name],registry=registry).validate(value)
    canonical(value)


def validate_protocol(config):
    frozen=read_json(PROJECT/'model/final-evaluation.schema.json')['properties']['protocol']['const']
    if config != frozen:
        raise AuditError('Final protocol differs from reviewed contract; revise evaluation policy explicitly')


def validate_final(e):
    schema_validate(e,'final-evaluation.schema.json')
    validate_protocol(e['protocol'])
    validate_evaluation(e['development_evidence'])
    if [r['role'] for r in e['results']] != e['protocol']['models']:
        raise AuditError('Final predictor inventory/order differs')
    clean={k:v for k,v in e.items() if k!='evidence_id'}
    if e['evidence_id'] != sha256(canonical(clean).encode()):
        raise AuditError('Final aggregate evidence identity differs')
    provenance=e['provenance']
    dev=e['development_evidence']
    if (provenance['selected_artifact_id'] != dev['selection']['selected_artifact_id']
            or provenance['feature_run_id'] != dev['provenance']['feature_run_id']
            or provenance['preparation_run_id'] != dev['provenance']['preparation_run_id']
            or provenance['final_protocol_sha256'] != sha256(canonical(e['protocol']).encode())):
        raise AuditError('Final/development provenance differs')
    if e['release_checks'] != release_checks(e):
        raise AuditError('Release checks differ from the declared evidence/rules')
    s=e['test_summary']
    for field in ('shots','goals','matches'):
        if sum(x[field] for x in s['composition']) != s[field]:
            raise AuditError('Final competition totals differ')
    if s['shots'] <= 0 or not 0 <= s['goals'] <= s['shots'] or s['prevalence'] != s['goals']/s['shots']:
        raise AuditError('Invalid final outcome counts')
    for r in e['results']:
        m=r['metrics']
        if any(m[k] != s[k] for k in ('shots','goals','prevalence')):
            raise AuditError('Predictors do not share test outcomes')
        if sum(b['shots'] for b in r['calibration_bins']) != s['shots'] or sum(b['goals'] for b in r['calibration_bins']) != s['goals']:
            raise AuditError('Calibration totals differ')
    for b in ('constant','full_logistic'):
        other=next(r for r in e['results'] if r['role']==b)
        selected=e['results'][0]
        for metric in ('log_loss','brier'):
            observed=selected['metrics'][metric]-other['metrics'][metric]
            if abs(observed-e['paired']['selected_minus_'+b][metric]['estimate']) > 1e-12:
                raise AuditError('Paired point estimate differs from score difference')
    forbidden={'match_id','match_ids','event_id','event_ids','vector','vectors','labels','players','location','raw_predictions','parameters'}
    def walk(value):
        if isinstance(value,dict):
            if forbidden.intersection(value):
                raise AuditError('Private records or parameters cannot enter final public evidence')
            for v in value.values():walk(v)
        elif isinstance(value,list):
            for v in value:walk(v)
    walk(e)


def number(v):
    return 'Unavailable' if v is None else f'{v:.6f}'


def ci(value):
    if value is None or value['interval'] is None:
        return 'Unavailable'
    return '['+', '.join(number(v) for v in value['interval'])+']'


def app_view(e):
    p=e['provenance']
    sections=[
        ('data','Male open-play foot shots from StatsBomb Open Data; valid embedded frame and observed opposing keeper required. Headers, penalties and missing/multiple keepers are excluded. No raw records are distributed.','development_evidence.exclusions'),
        ('features','Eight geometric/positional inputs: distance, goal opening angle, lateral offset, visible defender count, cone count, nearest visible defender distance, keeper-to-goal and keeper-to-shot distance. Only retained features affect this model.','development_evidence.feature_order'),
        ('leakage','Whole matches allocated without labels; training-only tuning and scaling, separate calibration and selection validation, frozen final test. No post-selection refit.','development_evidence.partitions'),
        ('experiments','Geometry, defender and full logistic baselines versus shallow XGBoost, each with identity or separately fitted sigmoid calibration. Validation selection is exploratory and separate from final testing.','development_evidence.experiments'),
        ('selection','The original predeclared selection decision is retained. Final testing cannot change the candidate or its calibration. Small differences do not establish superiority.','development_evidence.selection'),
        ('final-results','All final predictors use identical held-out rows. Lower log loss and Brier are better; intervals resample entire matches and retain shot weighting.','results'),
        ('calibration','Fixed probability bins compare predicted probabilities with observed goal rates. Empty bins are unavailable; sparse support and diagnostic review flags are explicit.','results.0.calibration_bins'),
        ('limitations','Partial frame visibility differs from represented browser scenes. Extra attackers and technique are omitted. Model scene changes are comparisons, not causal claims. Penalty 0.76 is a separate convention.','limitations'),
        ('reproduction','Exact immutable preparation, training and parity runs plus the pinned final protocol identify this evaluation. Complete comparisons and dated rights/product reviews are required.','provenance')]
    result={'schema_version':1,'contract_version':'xg-app-evidence/v1','evidence_id':e['evidence_id'],
            'training_run_id':p['training_run_id'],'selected_artifact_id':p['selected_artifact_id'],
            'release_status':e['release_checks']['status'],
            'sections':[{'id':k,'text':text,'evidence_path':path} for k,text,path in sections],
            'tables':{'final_test':e['results'],'validation':e['development_evidence']['experiments']},
            'charts':{'calibration':e['results'][0]['calibration_bins'],'slices':e['results'][0]['slices']},
            'paired':e['paired'],'scene_audit':e['scene_audit'],'limitations':e['limitations'],
            'links':{'report':'methodology.md','model_card':'model-card.md','reproduction':'docs/architecture/reference/xg-final-evaluation.md',
                     'training':'docs/reports/xg-training-methodology.md','rights':'docs/architecture/reference/statsbomb-rights.md'},
            'publication_authorized':False}
    schema_validate(result,'app-evidence.schema.json')
    return result


def render_report(e):
    validate_final(e)
    p=e['provenance'];s=e['test_summary']
    lines=['# Frozen xG final evaluation','',f"**Status:** {e['release_checks']['status']}; final test opened. Automated evidence does not authorize publication.",'',
           f"Evidence: `{e['evidence_id']}`. Training run: `{p['training_run_id']}`. Model: `{p['selected_artifact_id']}`.",'',
           '## Research question and development decisions','',
           'Does positional information improve probability estimation beyond shot geometry, and is the frozen pipeline fit for the defined non-commercial educational use? Actual goal outcomes are the labels; StatsBomb xG is neither an input nor a label. The original development evidence is preserved inside `final-evaluation.json`, and validation tables in `app-evidence.json` use that evidence directly.','',
           'Training-only exploration, feature distributions/correlations, bounded group CV, separate calibration and selection validation, coefficient interpretation and the original selection rationale are documented in the linked training report. Those development scores are not final-test scores.','',
           f"The frozen selection is **{e['development_evidence']['selection']['selected_model']}**. No refitting, retuning, calibration change or post-test candidate switch occurs. Constant prediction is frozen training prevalence; full logistic retains its previously selected preprocessing/calibration.",'',
           '## Population, counts and isolation','',
           e['population']+'. Source: [StatsBomb Open Data](https://github.com/hudl/open-data), independently modeled; no StatsBomb endorsement. Source revision: `'+p['source_revision']+'`.','',
           f"Final test: **{s['matches']} matches, {s['shots']} shots, {s['goals']} goals**, base rate {s['prevalence']:.4%}.",'',
           'Whole matches are isolated from training/calibration/selection. Historical split and manifest hashes are checked before test parsing. Missing/multiple keepers remain excluded; unseen defenders are not imputed. Coverage refers to partial embedded shot frames, not complete visible-area coverage from optional 360 files.','',
           '| Competition | Season | Matches | Shots | Goals | Base rate |','| --- | --- | ---: | ---: | ---: | ---: |']
    for r in s['composition']:
        lines.append(f"| {r['competition_id']} | {r['season_id']} | {r['matches']} | {r['shots']} | {r['goals']} | {r['prevalence']:.4%} |")
    lines += ['', '## Final probability scores','',
              'Log loss uses natural logarithms with 1e-12 metric-only probability clipping. Brier is mean squared probability error. Lower is better. Intervals are percentile 95% match-bootstrap intervals (1,000 resamples; seed 7421). Each draw samples whole matches with replacement, retains repeated-match multiplicity and weights scores by shots. All comparisons share draws.','',
              '| Role | Model | Log loss | 95% interval | Brier | 95% interval | Mean probability |',
              '| --- | --- | ---: | --- | ---: | --- | ---: |']
    for r in e['results']:
        lines.append(f"| {r['role']} | {r['model_version']} | {number(r['metrics']['log_loss'])} | {ci(r['uncertainty']['log_loss'])} | {number(r['metrics']['brier'])} | {ci(r['uncertainty']['brier'])} | {number(r['metrics']['mean_probability'])} |")
    lines += ['',f"Observed goal rate interval: {ci(e['results'][0]['uncertainty']['prevalence'])}.",'',
              '| Selected minus reference | Metric | Difference | 95% interval | Valid / skipped resamples |',
              '| --- | --- | ---: | --- | --- |']
    for name,record in sorted(e['paired'].items()):
        for metric,v in sorted(record.items()):lines.append(f"| {name} | {metric} | {number(v['estimate'])} | {ci(v)} | {v['valid_resamples']} / {v['skipped_resamples']} |")
    lines += ['', 'Intervals crossing zero do not establish an advantage. Passing the observed logistic guardrail does not prove equivalence. Validation selection comparisons remain exploratory.','',
              '## Calibration and slice support','',
              'Fixed tenths include probability 1 in the final bin. Sparse means fewer than 100 shots or 10 goals. Empty bins have null rates/intervals. One-match slices cannot estimate between-match uncertainty; replicates without slice observations are skipped and disclosed. Supported-bin residual intervals excluding zero trigger review, not a newly tuned calibrator. Slice comparisons are diagnostic and not corrected confirmatory tests.']
    for r in e['results']:
        lines += ['',f"### {r['role']} calibration",'', '| Bin | Matches | Shots | Goals | Predicted | Observed | Observed 95% interval | Residual 95% interval | Sparse | Review |',
                  '| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |']
        for b in r['calibration_bins']:
            lines.append(f"| {b['lower']:.1f}–{b['upper']:.1f} | {b['matches']} | {b['shots']} | {b['goals']} | {number(b['mean_probability'])} | {number(b['observed_rate'])} | {ci(b['observed_interval'])} | {ci(b['residual_interval'])} | {b['sparse']} | {b['review_flag']} |")
    lines += ['', '### Selected-model slices','',
              'The zero-defender nearest-distance category is missingness, not a measured pitch-diagonal defender. Detailed uncertainty and paired differences for all predictors are retained in the aggregate JSON.','',
              '| Feature / boundary | Matches | Shots | Goals | Log loss | 95% interval | Brier | Sparse |','| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |']
    for r in e['results'][0]['slices']:
        boundary=', '.join(f'{k}={r[k]}' for k in ('lower','upper','value','competition_id','season_id') if r[k] is not None)
        m=r['metrics'];u=r['uncertainty']
        lines.append(f"| {r['feature']} / {boundary} | {r['matches']} | {r['shots']} | {r['goals']} | {number(m['log_loss']) if m else 'Unavailable'} | {ci(u['log_loss']) if u else 'Unavailable'} | {number(m['brier']) if m else 'Unavailable'} | {r['sparse']} |")
    lines += ['', '## Synthetic scenes and support','',e['scene_audit']['support_method'],'',
              'Keeper/defender differences measure model response only. Individual tree plateaus, nonmonotonic responses and coordinate symmetry can all be valid. Unrealistic/extreme scenes and training/UI-bound differences need explicit scope/warning review.','',
              '| Invented scene | Status | Probability | Training support diagnostic | Outside marginals |','| --- | --- | ---: | --- | --- |']
    for r in e['scene_audit']['diagnostics']:
        lines.append(f"| {r['scene']} | {r['status']} | {number(r['probability'])} | {r['support_category']} | {r['outside_training_marginals']} |")
    lines += ['', '## Release checks and remaining review','',
              '| Predeclared predicate | Pass |','| --- | --- |']
    for k,v in sorted(e['release_checks']['predicates'].items()):lines.append(f'| {k} | {v} |')
    lines += ['', 'A failed statistical/scene predicate withholds the candidate. Completed withheld runs preserve evidence and exit with code 2. Passing predicates yields needs_review, not publication. Changes after opening require a revised evaluation protocol and defensible new evaluation; the existing test cannot be described as untouched.','',
              'Required review:', '']+[f'- {v}' for v in e['release_checks']['required_reviews']]
    lines += ['', '## Limitations','']+[f'- {v}' for v in e['limitations']]
    lines += ['', '## Reproduction and app handoff','',
              'Run evaluate_final.py with the exact immutable preparation, training and browser-parity directories, then compare two completed final runs with compare_final_runs.py. A deterministic test-opened record is written before outcome parsing and survives interrupted/failed attempts. Complete byte comparison is separate. Private test-predictions.json never enters public Git or deployed assets.','',
              'The bilingual #4 Methodology and results tab consumes app-evidence.json. Its section IDs and aggregate chart/table data derive from the same final evidence as this report. The app must surface model/version, uncertainty/sparse support and accepted limitations. Parameter-only distribution needs the documented non-commercial rights review, source link and official logo. Actual-product footer, bundles and network QA remain #4/#8.','',
              '[Training review](../../reports/xg-training-methodology.md) · [Final command guide](../../architecture/reference/xg-final-evaluation.md) · [Rights record](../../architecture/reference/statsbomb-rights.md)']
    return ('\n'.join(lines)+'\n').encode()


def render_card(e):
    r=e['results'][0];p=e['provenance']
    lines=['# Independent positional xG model card','',f"**Model:** {r['model_version']}; **artifact:** `{p['selected_artifact_id']}`.",'',
           f"**Evidence:** `{e['evidence_id']}`; **decision:** {e['release_checks']['status']}; publication requires dated review.",'',
           'Intended use: free non-commercial professional portfolio and educational scene comparisons. Not a StatsBomb model or endorsement. No claim of individual-player ability or causal effect.','',
           'Population: male open-play left/right-foot shots with valid embedded positional observations and one opposing keeper. Headers, penalties and missing/multiple keepers are excluded. Unseen defenders/attackers are not reconstructed.','',
           'Source: [StatsBomb Open Data](https://github.com/hudl/open-data), revision `'+p['source_revision']+'`. Conditional Hudl support scope and official source/logo obligations are recorded in docs/architecture/reference/statsbomb-rights.md. Public parameters, code and aggregate reports remain within the reviewed non-commercial scope. No raw source/shot records may be distributed.','',
           'Features, training-only exploration and experiment comparison are preserved in final-evaluation.json development_evidence. Training-only scaling/CV, separate calibration and selection validation precede this frozen match-held-out test. No post-selection refit.','',
           f"Selected retained inputs: {', '.join(e['development_evidence']['feature_order'][i] for i in next(x for x in e['development_evidence']['experiments'] if x['id']==r['model_version'])['feature_indices'])}.",'',
           f"Final log loss: {number(r['metrics']['log_loss'])}, 95% interval {ci(r['uncertainty']['log_loss'])}; Brier: {number(r['metrics']['brier'])}, 95% interval {ci(r['uncertainty']['brier'])}.",'',
           'See methodology.md for reference comparisons, paired uncertainty, calibration, supported/sparse slices and scene diagnostics. Those aggregate tables are generated from the same evidence; small differences are not automatically decisive.','',
           'Penalty estimates are a separate fixed 0.76 convention and are not learned or evaluated with the open-play model. Browser float32 tree semantics and independent numerical tolerances are retained. Missing/invalid input gives unsupported/unavailable, with no heuristic fallback.','',
           '## Limitations','']+[f'- {v}' for v in e['limitations']]
    lines += ['', '## Release and recovery','',
              'Statistical failures preserve a withheld result. Successful automated checks require independent complete reproduction, explicit calibration/slice/support review and a dated decision bound to model/evidence hashes. #4 still owns integrated production QA, bilingual attribution/logo and the mandatory methodology tab. Keep xG unpublished while any critical finding remains.','',
              'Reproduce with the locked Python environment, original immutable runs, evaluate_final.py and compare_final_runs.py; see docs/architecture/reference/xg-final-evaluation.md. Evidence verification must distinguish owner-run computations from independent recomputation.']
    return ('\n'.join(lines)+'\n').encode()


def public_outputs(e):
    validate_final(e)
    return {'final-evaluation.json':e,'release-checks.json':e['release_checks'],
            'app-evidence.json':app_view(e),'methodology.md':render_report(e),'model-card.md':render_card(e)}


def verify_views(directory):
    e=read_json(directory/'final-evaluation.json')
    for name,value in public_outputs(e).items():
        expected=value if isinstance(value,bytes) else canonical(value).encode()
        if (directory/name).read_bytes()!=expected:
            raise AuditError('Generated output differs from evidence: '+name)
    if read_json(directory/'protocol.json')!=e['protocol']:
        raise AuditError('Final protocol view differs')
    return e


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    try:
        from compare_final_runs import verified_final
        root,_,_=verified_final(args.run_dir)
        verify_views(root)
    except (AuditError,OSError,ValueError,KeyError,TypeError,ValidationError) as exc:
        print('FAIL: '+(str(exc) if isinstance(exc,AuditError) else 'Invalid final evidence or generated views'),file=sys.stderr)
        return 1
    print('PASS: aggregate evidence, report, model card and app views agree; no files modified')
    return 0


if __name__=='__main__':sys.exit(main())
