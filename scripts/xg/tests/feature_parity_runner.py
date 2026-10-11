"""Test-only bridge: receive shared synthetic scenes and evaluate Python independently."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from features import extract_metric_features, normalize_source_point  # noqa: E402

cases = json.load(sys.stdin)
json.dump([normalize_source_point(c["point"]) if c["mode"] == "source_point"
           else extract_metric_features(c["scene"]) for c in cases], sys.stdout, allow_nan=False)
