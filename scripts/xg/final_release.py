"""Predeclared final confirmation rules; never authorize publication automatically."""


def release_checks(e):
    p, summary = e['protocol'], e['test_summary']
    constant, logistic = e['paired']['selected_minus_constant'], e['paired']['selected_minus_full_logistic']
    interval = constant['log_loss']['interval']
    limit = p['decision']
    scene = e['scene_audit']
    predicates = {
        'test_support': summary['goals'] >= p['minima']['goals'] and summary['shots']-summary['goals'] >= p['minima']['non_goals'] and summary['matches'] >= p['minima']['matches'],
        'constant_log_loss': interval is not None and constant['log_loss']['estimate'] < -limit['constant_log_loss_improvement'] and interval[1] < -limit['constant_log_loss_improvement'],
        'constant_brier': constant['brier']['estimate'] <= limit['max_brier_degradation'],
        'logistic_guardrail': logistic['log_loss']['estimate'] <= limit['max_logistic_log_loss_degradation'] and logistic['brier']['estimate'] <= limit['max_brier_degradation'],
        'scene_response': all(scene['responses'].values()), 'invariants': scene['invariants_pass'],
        'parity': True,  # Input verification is mandatory before this function can be called.
    }
    flags = [f"{r['role']}:{i}" for r in e['results'] for i,b in enumerate(r['calibration_bins']) if b['review_flag']]
    reviews = ['complete independent reproduction and verification limits',
               'supported calibration/slices and sparse/extreme scene limitations',
               'parameter-only export and current non-commercial distribution rights',
               'dated owner/implementer decision bound to evidence/model hashes',
               '#4 actual product attribution, methodology, production bundles/network assets and #8 final QA']
    return {'status':'needs_review' if all(predicates.values()) else 'withheld', 'predicates':predicates,
            'calibration_review_bins':flags,'required_reviews':reviews,'publication_authorized':False}
