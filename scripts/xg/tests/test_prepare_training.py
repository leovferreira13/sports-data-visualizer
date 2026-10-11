import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from features import extract_metric_features
from ingest_statsbomb import AuditError
from prepare_training import allocate, fold_assignments, matches, split_matches, summary, validate_row
from run_io import protocol


def synthetic_rows(count=60):
    result = []
    features = extract_metric_features({"contract_version": "positional-features/v1", "shot_type": "open-play",
                                       "shooter": {"x": 84, "y": 34}, "goalkeepers": [{"x": 102, "y": 34}],
                                       "defenders": [{"x": 93, "y": 34}], "observation": "embedded-frame"})
    for mid in range(1, count + 1):
        for i in range(2):
            result.append({"competition_id": 1 + mid // 21, "season_id": 1, "match_id": mid,
                           "event_id": f"invented-{mid}-{i}", "is_goal": i, **copy.deepcopy(features)})
    return result


class PreparationTests(unittest.TestCase):
    def test_match_partition_and_label_independence(self):
        rows = synthetic_rows()
        config = protocol()
        split = split_matches(rows, config)
        self.assertEqual(set(split.values()), {"train", "calibration", "selection", "test"})
        for row in rows:
            row["is_goal"] = 1 - row["is_goal"]
        self.assertEqual(split, split_matches(list(reversed(rows)), config))
        train = [r for r in rows if split[r["match_id"]] == "train"]
        self.assertEqual(set(fold_assignments(train, config).values()), set(range(5)))

    def test_largest_remainder_and_insufficient_strata(self):
        self.assertEqual(allocate(80, [6, 1, 1, 2]), [48, 8, 8, 16])
        self.assertEqual(sum(allocate(9, [6, 1, 1, 2])), 9)
        with self.assertRaises(AuditError):
            split_matches(synthetic_rows(2), protocol())

    def test_test_summary_never_reports_goals(self):
        result = summary(synthetic_rows(), labels=False)
        self.assertNotIn("goals", result)
        self.assertNotIn("prevalence", result)
        self.assertTrue(all("goals" not in x for x in result["composition"]))

    def test_invalid_vectors_missingness_duplicates_and_roles(self):
        row = synthetic_rows()[0]
        mutations = [lambda r: r.update(is_goal=True), lambda r: r['vector'].__setitem__(0, float('nan')),
                     lambda r: r['metadata'].update(defender_visibility='represented'),
                     lambda r: r.update(vector=r['vector'][1:]), lambda r: r['features'].update(shot_distance_m=2)]
        for mutation in mutations:
            changed = copy.deepcopy(row)
            mutation(changed)
            with self.assertRaises(AuditError):
                validate_row(changed)
        with self.assertRaises(AuditError):
            matches([row, row])
        with self.assertRaises(AuditError):
            matches([row, {**row, 'event_id':'invented-other', 'competition_id':3}])


if __name__ == '__main__':
    unittest.main()
