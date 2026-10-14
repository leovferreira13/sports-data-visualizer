"""Decision contract for the frozen current-versus-monotonic comparison."""

from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_monotonic_pair import (CONSTRAINTS, LOG_LOSS_LIMIT, assert_identity, assert_output_allowed,
                                    assert_selection_counts, direction_violation_count, jump_gate_passes,
                                    mean_log_loss, pair_decisions, render_pair_report, require_constraints,
                                    revised_decision, write_outputs)
from ingest_statsbomb import AuditError, sha256
from run_io import PROJECT


def evaluation(evidence="f62228e611a9712acaac4abcbc61b0f3ffc1ec0b0880e111bd0aa447f872dee8", seed=42):
    return {
        "evidence_id": evidence,
        "original_training_run_id": "222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a",
        "provenance": {"split_sha256": "64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1"},
        "protocol": {"original_training_protocol": {"seed": seed},
                     "candidate": {"monotone_constraints": list(CONSTRAINTS)}},
        "models": {
            "full_xgboost": {"artifact_id": "758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a"},
            "full_monotonic_xgboost": {"artifact_id": "e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce"},
        },
    }


def manifest():
    return {"run_id": "222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a",
            "split_sha256": "64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1"}


class CompareMonotonicPairTests(unittest.TestCase):
    def test_revised_rule_accepts_a_small_log_loss_increase_without_direction_violations(self):
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=0.001,
            distance_violations=0, angle_violations=0)
        self.assertEqual(status, "recommend_replacement")

    def test_log_loss_limit_is_inclusive_and_the_next_step_retains(self):
        at_limit, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=LOG_LOSS_LIMIT,
            distance_violations=0, angle_violations=0)
        above, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True,
            log_loss_increase=float(np.nextafter(LOG_LOSS_LIMIT, 1)),
            distance_violations=0, angle_violations=0)
        self.assertEqual(at_limit, "recommend_replacement")
        self.assertEqual(above, "retain")
        self.assertEqual(LOG_LOSS_LIMIT, 0.005)

    def test_distance_increase_above_tolerance_is_a_direction_violation_and_retains(self):
        violations = direction_violation_count([0.20, 0.20 + 2e-7], direction=-1)
        self.assertEqual(violations, 1)
        self.assertEqual(direction_violation_count([0.20, 0.20 + 1e-8], direction=-1), 0)
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=0.001,
            distance_violations=violations, angle_violations=0)
        self.assertEqual(status, "retain")

    def test_identity_seed_and_artifact_mismatches_raise_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            before = sha256((PROJECT / "model" / "selected-model.json").read_bytes())
            with self.assertRaises(AuditError):
                assert_identity(evaluation(evidence="0" * 64), manifest())
                write_outputs(output, {"pair-metrics.json": {}})
            self.assertEqual(list(output.iterdir()), [])
            with self.assertRaises(AuditError):
                assert_identity(evaluation(seed=7), manifest())
            changed = evaluation()
            changed["models"]["full_monotonic_xgboost"]["artifact_id"] = "a" * 64
            with self.assertRaises(AuditError):
                assert_identity(changed, manifest())
            self.assertEqual(sha256((PROJECT / "model" / "selected-model.json").read_bytes()), before)

    def test_selection_count_mismatch_fails_closed(self):
        rows = [{"is_goal": 1}, {"is_goal": 0}]
        assert_selection_counts(rows, 2, 1)
        with self.assertRaises(AuditError):
            assert_selection_counts(rows, 3, 1)
        with self.assertRaises(AuditError):
            assert_selection_counts(rows, 2, 2)

    def test_only_the_declared_monotone_tuple_is_accepted(self):
        require_constraints(CONSTRAINTS)
        with self.assertRaises(AuditError):
            require_constraints([0, 1, 0, 0, 0, 0, 0, 0])

    def test_side_by_side_decisions_show_when_the_jump_gate_changes_the_result(self):
        current = {"pairs": 10, "large_jump_rate": 0.10, "p95_jump": 0.02}
        candidate = {"pairs": 10, "large_jump_rate": 0.09, "p95_jump": 0.02}
        self.assertFalse(jump_gate_passes(candidate, current))
        decisions = pair_decisions(
            identity_ok=True, pairs_equal=True, primary_available=True,
            log_loss_upper=0.001, brier_upper=0.0001, directions_pass=True,
            jump_passes=False, log_loss_increase=0.001,
            distance_violations=0, angle_violations=0)
        self.assertEqual(decisions["original_predeclared"]["status"], "retain")
        self.assertEqual(decisions["revised"]["status"], "recommend_replacement")
        self.assertTrue(decisions["depends_on_revision"])
        self.assertTrue(decisions["original_predeclared"]["includes_jump_reduction_gate"])
        self.assertFalse(decisions["revised"]["includes_jump_reduction_gate"])
        report = render_pair_report({
            "decisions": decisions, "log_loss_increase": 0.001,
            "log_loss_upper": 0.001, "brier_upper": 0.0001,
            "metrics": {name: {"log_loss": 0.2, "brier": 0.06, "distance_violations": 0,
                               "angle_violations": 0, "large_jump_rate": 0.1, "p95_jump": 0.02}
                        for name in ("full_xgboost", "full_monotonic_xgboost")},
        })
        self.assertIn("25% jump-reduction gate", report)
        self.assertIn("depends on the revision: **true**", report)

    def test_mean_log_loss_increase_feeds_the_revised_rule(self):
        labels = np.array([0, 1, 0, 1])
        current = mean_log_loss(labels, np.array([0.2, 0.8, 0.2, 0.8]))
        worse = mean_log_loss(labels, np.full(4, 0.5))
        self.assertGreater(worse - current, 0)
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=worse - current,
            distance_violations=0, angle_violations=0)
        self.assertEqual(status, "retain")

    def test_writer_refuses_the_published_model_directory(self):
        with self.assertRaises(AuditError):
            assert_output_allowed(PROJECT / "model")
        with tempfile.TemporaryDirectory() as tmp:
            write_outputs(tmp, {"pair-metrics.json": {"decisions": {"revised": {"status": "recommend_replacement"}}}})
            self.assertTrue((Path(tmp) / "pair-metrics.json").is_file())
            self.assertEqual(sha256((PROJECT / "model" / "selected-model.json").read_bytes()),
                             "c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d")


if __name__ == "__main__":
    unittest.main()
