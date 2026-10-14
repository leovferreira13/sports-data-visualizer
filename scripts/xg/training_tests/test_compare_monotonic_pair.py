"""Decision contract for the frozen current-versus-monotonic comparison."""

from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_monotonic_pair import (CONSTRAINTS, PREDECLARED_GATES, assert_identity, assert_output_allowed,
                                    assert_selection_counts, direction_violation_count, mean_log_loss,
                                    original_decision, pair_decisions, render_pair_report, require_constraints,
                                    require_decision_limits, revised_decision, write_outputs)
from ingest_statsbomb import AuditError, sha256
from run_io import PROJECT, read_json


def json_protocol():
    return read_json(PROJECT / "model" / "behavior-protocol.json")


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


def phase_a_limits():
    return {
        "max_log_loss_degradation": 0.005,
        "max_brier_degradation": 0.001,
        "min_jump_rate_reduction": 0.25,
        "one_sided_confidence": 0.95,
    }


def primary(rate, p95, pairs=10):
    return {"pairs": pairs, "large_jump_rate": rate, "p95_jump": p95}


def passing_record():
    return {
        "quality": {
            "paired_with_current": {
                "log_loss": {"upper_95": 0.001},
                "brier": {"upper_95": 0.0001},
            },
            "beats_constant": True,
            "calibration_bins": [],
            "slices": [],
        },
        "behavior": {"pooled": {"primary": primary(0.05, 0.01)}, "partial_direction_pass": True},
        "scene_audit": {"invariants_pass": True},
        "parity": {"status": "pass"},
        "native_export_pass": True,
    }


def load_gates():
    """Import the real gates function. Stub only packages this environment does not have."""
    import importlib.util
    import sys
    import types

    def installed(name):
        if name in sys.modules and getattr(sys.modules[name], "__spec__", None) is not None:
            return True
        try:
            return importlib.util.find_spec(name) is not None
        except (ModuleNotFoundError, AttributeError, ValueError):
            return False

    def package(name):
        mod = sys.modules.get(name)
        if mod is None:
            mod = types.ModuleType(name)
            sys.modules[name] = mod
        mod.__path__ = getattr(mod, "__path__", [])
        return mod

    def prepare_stubs():
        for name in ("behavior_statistics", "training", "model_export", "evaluation", "final_statistics"):
            sys.modules.pop(name, None)
        if not installed("scipy"):
            scipy = package("scipy")
            stats = package("scipy.stats")
            special = package("scipy.special")
            stats.spearmanr = lambda *_args, **_kwargs: (0.0, 1.0)
            special.expit = lambda value: value
            scipy.stats = stats
            scipy.special = special
        if not installed("sklearn"):
            package("sklearn")
            package("sklearn.exceptions").ConvergenceWarning = Warning
            package("sklearn.linear_model").LogisticRegression = object
            package("sklearn.pipeline").Pipeline = object
            package("sklearn.preprocessing").StandardScaler = object
        if not installed("threadpoolctl"):
            package("threadpoolctl").threadpool_limits = lambda *_args, **_kwargs: None
        if not installed("xgboost"):
            package("xgboost").XGBClassifier = object

    try:
        from behavior_statistics import gates
        return gates
    except ModuleNotFoundError:
        prepare_stubs()
        from behavior_statistics import gates
        return gates


class CompareMonotonicPairTests(unittest.TestCase):
    def test_revised_rule_accepts_a_small_log_loss_increase_without_direction_violations(self):
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=0.001,
            distance_violations=0, angle_violations=0, limits=phase_a_limits())
        self.assertEqual(status, "recommend_replacement")

    def test_log_loss_limit_is_inclusive_and_comes_from_the_protocol(self):
        committed = require_decision_limits(
            json_protocol())
        self.assertEqual(committed["max_log_loss_degradation"], 0.005)
        at_limit, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True,
            log_loss_increase=committed["max_log_loss_degradation"],
            distance_violations=0, angle_violations=0, limits=committed)
        above, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True,
            log_loss_increase=float(np.nextafter(committed["max_log_loss_degradation"], 1)),
            distance_violations=0, angle_violations=0, limits=committed)
        tighter = dict(committed)
        tighter["max_log_loss_degradation"] = 0.001
        tightened, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=0.002,
            distance_violations=0, angle_violations=0, limits=tighter)
        self.assertEqual(at_limit, "recommend_replacement")
        self.assertEqual(above, "retain")
        self.assertEqual(tightened, "retain")

    def test_distance_increase_above_tolerance_is_a_direction_violation_and_retains(self):
        violations = direction_violation_count([0.20, 0.20 + 2e-7], direction=-1)
        self.assertEqual(violations, 1)
        self.assertEqual(direction_violation_count([0.20, 0.20 + 1e-8], direction=-1), 0)
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=0.001,
            distance_violations=violations, angle_violations=0, limits=phase_a_limits())
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
        gates = load_gates()
        limits = phase_a_limits()
        record = passing_record()
        record["behavior"]["pooled"]["primary"] = primary(0.09, 0.02)
        current = {"pooled": {"primary": primary(0.10, 0.02)}}
        result = gates(record, current, {"decision": limits})
        self.assertEqual(result["failures"], ["interactive_improvement"])
        decisions = pair_decisions(
            identity_ok=True, pairs_equal=True, gates_result=result, limits=limits,
            log_loss_increase=0.001, distance_violations=0, angle_violations=0)
        self.assertEqual(decisions["original_predeclared"]["status"], "retain")
        self.assertEqual(decisions["revised"]["status"], "recommend_replacement")
        self.assertTrue(decisions["depends_on_revision"])
        self.assertTrue(decisions["original_predeclared"]["includes_jump_reduction_gate"])
        self.assertFalse(decisions["revised"]["includes_jump_reduction_gate"])
        self.assertEqual(decisions["original_predeclared"]["jump_reduction_required"], 0.25)
        report = render_pair_report({
            "decisions": decisions, "log_loss_increase": 0.001,
            "log_loss_upper": 0.001, "brier_upper": 0.0001,
            "metrics": {name: {"log_loss": 0.2, "brier": 0.06, "distance_violations": 0,
                               "angle_violations": 0, "large_jump_rate": 0.1, "p95_jump": 0.02}
                        for name in ("full_xgboost", "full_monotonic_xgboost")},
        })
        self.assertIn("25% jump-reduction gate", report)
        self.assertIn("Predeclared gate failed: interactive_improvement", report)
        self.assertIn("depends on the revision: **true**", report)

    def test_original_decision_fails_when_any_omitted_gate_fails(self):
        gates = load_gates()
        limits = phase_a_limits()
        current = {"pooled": {"primary": primary(0.10, 0.02)}}
        omitted = {
            "constant_reference": lambda record: record["quality"].__setitem__("beats_constant", False),
            "partial_directions": lambda record: record["behavior"].__setitem__("partial_direction_pass", False),
            "invariants": lambda record: record["scene_audit"].__setitem__("invariants_pass", False),
            "parity": lambda record: record["parity"].__setitem__("status", "fail"),
            "native_export": lambda record: record.__setitem__("native_export_pass", False),
        }
        self.assertEqual(set(omitted), set(PREDECLARED_GATES) - {
            "log_loss", "brier", "primary_segments_available", "interactive_improvement"})
        for name, mutate in omitted.items():
            record = passing_record()
            mutate(record)
            result = gates(record, current, {"decision": limits})
            self.assertIn(name, result["failures"], name)
            status, reasons = original_decision(result, limits)
            self.assertEqual(status, "retain", name)
            self.assertIn(f"Predeclared gate failed: {name}", reasons)
            decisions = pair_decisions(
                identity_ok=True, pairs_equal=True, gates_result=result, limits=limits,
                log_loss_increase=0.001, distance_violations=0, angle_violations=0)
            self.assertEqual(decisions["revised"]["status"], "recommend_replacement", name)
            self.assertTrue(decisions["depends_on_revision"], name)
        passing = gates(passing_record(), current, {"decision": limits})
        self.assertEqual(original_decision(passing, limits)[0], "recommend_replacement")
        missing = dict(passing)
        missing["predicates"] = {key: value for key, value in passing["predicates"].items()
                                 if key != "native_export"}
        self.assertEqual(original_decision(missing, limits)[0], "insufficient_evidence")

    def test_probability_limits_come_from_protocol_decision(self):
        gates = load_gates()
        current = {"pooled": {"primary": primary(0.10, 0.02)}}
        record = passing_record()
        record["quality"]["paired_with_current"]["log_loss"]["upper_95"] = 0.002
        loose = gates(record, current, {"decision": phase_a_limits()})
        self.assertNotIn("log_loss", loose["failures"])
        tight_limits = dict(phase_a_limits())
        tight_limits["max_log_loss_degradation"] = 0.001
        tight = gates(record, current, {"decision": tight_limits})
        self.assertIn("log_loss", tight["failures"])
        self.assertEqual(original_decision(tight, tight_limits)[0], "retain")
        self.assertEqual(original_decision(loose, phase_a_limits())[0], "recommend_replacement")
        with self.assertRaises(AuditError):
            require_decision_limits({"decision": {"max_log_loss_degradation": 0.005}})

    def test_mean_log_loss_increase_feeds_the_revised_rule(self):
        labels = np.array([0, 1, 0, 1])
        current = mean_log_loss(labels, np.array([0.2, 0.8, 0.2, 0.8]))
        worse = mean_log_loss(labels, np.full(4, 0.5))
        self.assertGreater(worse - current, 0)
        status, _reasons = revised_decision(
            identity_ok=True, pairs_equal=True, log_loss_increase=worse - current,
            distance_violations=0, angle_violations=0, limits=phase_a_limits())
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
