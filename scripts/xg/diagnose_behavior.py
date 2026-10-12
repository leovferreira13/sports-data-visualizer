#!/usr/bin/env python3
"""Diagnose the published artifact on invented scenes, without any fitting or rows."""

import argparse
from pathlib import Path
import sys

from jsonschema import ValidationError

from behavior_io import PUBLISHED, research_codes, research_protocol
from behavior_sweeps import evaluate_sweeps
from check_browser_inference import verify
from evaluate_behavior import parity_cases
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import validate_envelope
from run_io import PROJECT, publish, read_json


def diagnose(output_dir, browser=False):
    config, codes = research_protocol(), research_codes()
    envelope = read_json(PUBLISHED)
    validate_envelope(envelope)
    final = read_json(PROJECT/'model/final-evaluation-protocol.json')
    behavior, traces = evaluate_sweeps(envelope, [], config, final)
    parity = verify(envelope, browser, parity_cases([], config))
    evidence = {'schema_version': 1, 'scope': 'published-artifact-invented-scenes-only',
                'artifact_id': envelope['artifact_id'], 'behavior': behavior, 'parity': parity,
                'training_or_test_rows_accessed': False, 'quality_evaluated': False,
                'publication_authorized': False, 'support': 'no private training rows; empirical support unassessed'}
    def guard():
        if research_codes() != codes or read_json(PUBLISHED) != envelope:
            raise AuditError('Published artifact or diagnostic code changed')
    return publish(output_dir, PUBLISHED.parent, 'behavior-published-diagnostic',
                   {'published-behavior.json': evidence, 'protocol.json': config, 'sweep-details.json': traces},
                   {'artifact_id': envelope['artifact_id'], 'code_sha256': codes,
                    'protocol_sha256': sha256(canonical(config).encode())}, guard)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--browser', action='store_true')
    args = parser.parse_args()
    try:
        root = diagnose(args.output_dir, args.browser)
    except (AuditError, OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
        print('FAIL: '+(str(exc) if isinstance(exc, AuditError) else 'Invalid diagnostic input or output'), file=sys.stderr)
        return 1
    print(f'Complete immutable published-model diagnostic: {root}; no fitting or empirical quality claims')
    return 0


if __name__ == '__main__':
    sys.exit(main())
