"""Validate aggregate research evidence and derive the comparison report."""

from jsonschema import validate

from features import FEATURE_NAMES
from ingest_statsbomb import AuditError, canonical, sha256
from run_io import PROJECT, read_json


def evidence_identity(e):
    return sha256(canonical({k: v for k, v in e.items() if k != 'evidence_id'}).encode())


def validate_behavior(e):
    validate(e, read_json(PROJECT/'model/behavior-evaluation.schema.json'))
    if e['evidence_id'] != evidence_identity(e) or e['feature_order'] != list(FEATURE_NAMES):
        raise AuditError('Research evidence identity or feature order differs')
    validate(e['protocol'], read_json(PROJECT/'model/behavior-protocol.schema.json'))
    if e['selection']['publication_authorized'] is not False:
        raise AuditError('Research evidence cannot authorize publication')
    forbidden = {'event_id', 'match_id', 'match_ids', 'vector', 'vectors', 'location', 'players',
                 'labels', 'raw_predictions', 'records', 'feature_deltas', 'coordinates'}
    def walk(item, parent=None):
        if isinstance(item, dict):
            disallowed = forbidden.intersection(item)
            if parent == 'case_counts' and type(item.get('vectors')) is int:
                disallowed.discard('vectors')
            if disallowed or ('scene' in item and not isinstance(item['scene'], str)):
                raise AuditError('Private row/trace fields in aggregate research evidence')
            for key, value in item.items():
                walk(value, key)
        elif isinstance(item, list):
            for value in item:
                walk(value, parent)
    walk(e)
    if set(e['models']) != {'full_xgboost', 'full_logistic', 'full_monotonic_xgboost'}:
        raise AuditError('Research evidence omits a declared model')
    from behavior_statistics import gates, select_candidates
    for name in sorted(e['models']):
        record = e['models'][name]
        if name != 'full_xgboost' and record['gates'] != gates(record, e['models']['full_xgboost']['behavior'], e['protocol']):
            raise AuditError('Research gates differ from their evidence')
    expected = select_candidates(e['models'], e['protocol'])
    if e['selection'] != expected:
        raise AuditError('Research selection differs from its gates')


def render_report(e):
    validate_behavior(e)
    lines = ['# xG behavior comparison', '', '**Scope:** adaptive exploratory selection evidence. '
             'The previous final test was opened; it is not re-opened or relabeled untouched.', '',
             f"Evidence: `{e['evidence_id']}`. Protocol: `{e['provenance']['protocol_sha256']}`.", '',
             f"Disposition: **{e['selection']['status']}**. Recommendation: **{e['selection']['recommended_model'] or 'none'}**.", '',
             '## Probability and interaction comparison', '',
             '| Model | Log loss | Brier | Isolated direction violations | Primary pairs | >2pp jump rate | p95 jump |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name in sorted(e['models']):
        record = e['models'][name]
        m, b = record['quality']['metrics'], record['behavior']
        primary = b['pooled']['primary']
        def number(value):
            return 'Insufficient support' if value is None else f'{value:.8f}'
        lines.append(f"| {name} | {m['log_loss']:.8f} | {m['brier']:.8f} | "
                     f"{sum(s['violations'] for s in b['isolated'])} | {primary['pairs']} | "
                     f"{number(primary['large_jump_rate'])} | {number(primary['p95_jump'])} |")
    lines += ['', '## Decisions and review flags', '',
              'Quality margins are absolute score degradations of 0.005 log loss and 0.001 Brier, '
              'using one-sided 95% paired-match bootstrap upper bounds. Interactive improvement requires '
              'a 25% lower >0.02 jump rate without higher p95 jump size on supported continuous ordinary paths. '
              'When the current jump rate is zero, the candidate also needs zero rate and strictly smaller p95. '
              'These margins are product tradeoffs, not universal scientific constants.', '']
    for name in sorted(e['selection']['candidate_checks']):
        checks = e['selection']['candidate_checks'][name]
        lines += [f"- **{name}:** {'eligible' if checks['eligible'] else 'does not qualify'}. "
                  f"Failed gates: {', '.join(checks['failures']) or 'none'}. "
                  f"Required reviews: {', '.join(checks['required_reviews']) or 'none'}."]
    lines += ['', '## Plateaus, discontinuities and support', '',
              'All full-probability isolated sweeps, plateau share/span and jump summaries are in '
              '`behavior-evaluation.json`. Isolated vectors hold six other features fixed and may be '
              'physically inconsistent. Physical paths record all eight deltas privately; their reversals '
              'are not automatically partial-direction violations. Raw/calibrated/exported candidate '
              'directions and native/export errors are recorded separately.', '',
              '| Model | Segment category | Pairs | >2pp jump rate | p95 jump |',
              '| --- | --- | ---: | ---: | ---: |']
    for name in sorted(e['models']):
        record = e['models'][name]
        for category in sorted(record['behavior']['pooled']):
            values = record['behavior']['pooled'][category]
            lines.append(f"| {name} | {category} | {values['pairs']} | "
                         f"{number(values['large_jump_rate'])} | {number(values['p95_jump'])} |")
    lines += ['', 'Outside-reference, insufficient-reference, extreme and count-transition segments '
              'remain visible above and in per-path summaries. Support is a training-only nearest-neighbor '
              'diagnostic, not calibration evidence or a runtime rejection rule. Sparse calibration/slices '
              'and supported adverse differences are retained with review flags in the aggregate JSON.', '',
              '## Logistic interpretation and goalkeeper defaults', '',
              'Frozen standardized logistic coefficients, scales, calibration and train-only correlations '
              'are recorded in `logistic_diagnostics`. Coefficients are conditional associations under '
              'correlation/regularization, not causal effects. Continuous inputs give continuous logistic '
              'responses; cone/count transitions can still jump. The monotonic tree candidate can still plateau.', '',
              'Keeper advance/lateral and extreme fixtures use actual retained features. No default keeper '
              'position is changed. Any proposed default change needs a separate contextual support review.', '',
              '## Verification and next boundary', '',
              'Node executes the browser-targeted TypeScript bundle by default; optional Chromium execution '
              'is recorded explicitly. Parity does not establish predictive fitness. Parameters, row predictions, '
              'training anchors and complete sweep traces remain local. The entire research run must reproduce '
              'before an evidence-backed disposition is accepted.', '',
              'A genuinely unused holdout must be reserved before fitting through the separate reservation '
              'command. Local match overlap can be checked; unknown external prior use cannot be mechanically '
              'proved and requires an explicit provenance declaration. No candidate can automatically replace '
              'the published model. Without independent evidence, any recommendation is exploratory.', '',
              *[f'- {note}' for note in e['limitations']], '']
    return '\n'.join(lines).encode()
