"""Probability metrics and paired match bootstrap, never a test-data loader."""

import numpy as np
from scipy.stats import spearmanr

from features import FEATURE_NAMES
from ingest_statsbomb import AuditError


def checked(y, p):
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    if (y.ndim != 1 or p.shape != y.shape or not len(y) or not np.isin(y, [0, 1]).all()
            or not np.isfinite(p).all() or (p < 0).any() or (p > 1).any()):
        raise AuditError("Invalid probability evaluation inputs")
    return y, p


def losses(y, p, clip):
    y, p = checked(y, p)
    q = np.clip(p, clip, 1 - clip)
    return {"log_loss": -(y * np.log(q) + (1 - y) * np.log1p(-q)), "brier": (p - y) ** 2}


def metrics(y, p, config):
    y, p = checked(y, p)
    values = {k: float(v.mean()) for k, v in losses(y, p, config["metric_clip"]).items()}
    return {**values, "shots": len(y), "goals": int(y.sum()),
            "prevalence": float(y.mean()), "mean_probability": float(p.mean())}


def bins(y, p, config):
    y, p = checked(y, p)
    assignments = np.minimum((p * 10).astype(int), 9)
    result = []
    for i in range(10):
        take = assignments == i
        n = int(take.sum())
        result.append({"lower": i / 10, "upper": (i + 1) / 10,
                       "upper_inclusive": i == 9, "shots": n, "goals": int(y[take].sum()),
                       "mean_probability": float(p[take].mean()) if n else None,
                       "observed_rate": float(y[take].mean()) if n else None,
                       "sparse": n < config["sparse"]["shots"] or int(y[take].sum()) < config["sparse"]["goals"]})
    return result


def paired_difference(rows, y, a, b, config):
    la, lb = losses(y, a, config["metric_clip"]), losses(y, b, config["metric_clip"])
    mids = sorted({r["match_id"] for r in rows})
    lookup = {mid: i for i, mid in enumerate(mids)}
    group = np.array([lookup[r["match_id"]] for r in rows])
    counts = np.bincount(group, minlength=len(mids))
    sums = {k: np.bincount(group, weights=la[k] - lb[k], minlength=len(mids)) for k in la}
    rng = np.random.default_rng(config["bootstrap"]["seed"])
    replicates = {k: [] for k in sums}
    for _ in range(config["bootstrap"]["resamples"]):
        weights = np.bincount(rng.integers(0, len(mids), len(mids)), minlength=len(mids))
        denominator = weights @ counts
        for key, values in sums.items():
            replicates[key].append(float(weights @ values / denominator))
    alpha = (1 - config["bootstrap"]["confidence"]) / 2
    return {key: {"difference": float((la[key] - lb[key]).mean()),
                  "interval": np.quantile(replicates[key], [alpha, 1 - alpha]).tolist()}
            for key in sums}


def slice_masks(rows, config):
    x = np.asarray([r["vector"] for r in rows])
    for name, edges in config["bins"].items():
        values = x[:, FEATURE_NAMES.index(name)]
        for i, (lower, upper) in enumerate(zip(edges, edges[1:])):
            take = (values >= lower) & ((values <= upper if i == len(edges) - 2 else values < upper)
                                       if upper is not None else True)
            yield name, {"lower": lower, "upper": upper}, take
    for count in range(11):
        yield "visible_defender_count", {"value": count}, x[:, 3] == count
    for cid, sid in sorted({(r["competition_id"], r["season_id"]) for r in rows}):
        yield "competition_season", {"competition_id": cid, "season_id": sid}, np.array([
            r["competition_id"] == cid and r["season_id"] == sid for r in rows])


def slices(rows, y, p, config):
    result = []
    y, p = checked(y, p)
    for name, boundary, mask in slice_masks(rows, config):
        n, g = int(mask.sum()), int(y[mask].sum())
        result.append({"feature": name, **boundary, "shots": n, "goals": g,
                       "sparse": n < config["sparse"]["shots"] or g < config["sparse"]["goals"],
                       "metrics": metrics(y[mask], p[mask], config) if n else None})
    return result


def correlation(x, rank=False):
    if not len(x):
        return [[None] * x.shape[1] for _ in range(x.shape[1])]
    matrix = []
    for i in range(x.shape[1]):
        row = []
        for j in range(x.shape[1]):
            if np.ptp(x[:, i]) == 0 or np.ptp(x[:, j]) == 0:
                value = None
            elif rank:
                value = float(spearmanr(x[:, i], x[:, j]).statistic)
            else:
                value = float(np.corrcoef(x[:, i], x[:, j])[0, 1])
            row.append(value)
        matrix.append(row)
    return matrix


def explore(rows, config):
    x = np.asarray([r["vector"] for r in rows], dtype=float)
    y = np.asarray([r["is_goal"] for r in rows])
    summaries = {}
    for i, name in enumerate(FEATURE_NAMES):
        observed = x[:, 3] != 0 if i == 5 else np.ones(len(rows), dtype=bool)
        v = x[observed, i]
        summaries[name] = {"shots": len(v), "min": float(v.min()) if len(v) else None,
                           "max": float(v.max()) if len(v) else None,
                           "quantiles": np.quantile(v, [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).tolist() if len(v) else None}
    rates = []
    for name, boundary, mask in slice_masks(rows, config):
        n, g = int(mask.sum()), int(y[mask].sum())
        rates.append({"feature": name, **boundary, "shots": n, "goals": g,
                      "observed_rate": g / n if n else None,
                      "sparse": n < config["sparse"]["shots"] or g < config["sparse"]["goals"]})
    # The sentinel is excluded from continuous distance distributions/correlations.
    observed = x[:, 3] != 0
    return {"partition": "train", "features": list(FEATURE_NAMES), "distributions": summaries,
            "zero_defender_sentinel_shots": int((~observed).sum()),
            "correlation_population": "training rows with at least one observed defender",
            "pearson": correlation(x[observed]), "spearman": correlation(x[observed], True),
            "goal_rates": rates, "visibility": "partial embedded frames; unseen players not imputed",
            "support_note": "Marginal ranges do not establish joint scene support"}
