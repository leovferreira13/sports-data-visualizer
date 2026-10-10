# Prediction and model data

**Status:** candidate design; model choice is gated by Issue #3.

`lib/features.ts` is planned to turn a `Scenario` into named features with explicit units. Candidate features include shot distance and angle, nearest defender distance, defenders in the shot cone, and goalkeeper position relative to goal and shot line. Include a feature only if it can be calculated consistently from both training data and the interactive field.

`lib/predict.ts` should expose a deterministic `predict(features, modelMetadata)` result with a probability in `[0, 1]` and model ID. Versioned metadata should identify data/model provenance, licensing, supported shot population, actual features, penalty treatment, evaluation, calibration and omissions. A lightweight `model/model.json` can be imported by the browser if its size and format permit it.

Parent #3 selects our own regularized logistic regression baseline and constrained XGBoost positional candidate, trained offline from legally usable StatsBomb Open Data. The [local ingestion audit](statsbomb-ingestion.md) measures eligible shot and visibility coverage first; #10 defines the shared feature contract and #11 owns training with match-based train/validation/test separation. Check held-out calibration and scenario behavior in #13 before release. None of these model components is implemented by ingestion. The production page must never suggest goalkeeper or defender movement changes xG unless the model actually uses them.

**Learning note:** inference means evaluating a trained model on new input. Training is the separate process that derives its parameters. Running inference in the browser avoids a server round-trip but requires a small supported artifact and exactly matching feature calculations.
