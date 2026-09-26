# Prediction and model data

**Status:** candidate design; model choice is gated by Issue #3.

`lib/features.ts` is planned to turn a `Scenario` into named features with explicit units. Candidate features include shot distance and angle, nearest defender distance, defenders in the shot cone, and goalkeeper position relative to goal and shot line. Include a feature only if it can be calculated consistently from both training data and the interactive field.

`lib/predict.ts` should expose a deterministic `predict(features, modelMetadata)` result with a probability in `[0, 1]` and model ID. Versioned metadata should identify data/model provenance, licensing, supported shot population, actual features, penalty treatment, evaluation, calibration and omissions. A lightweight `model/model.json` can be imported by the browser if its size and format permit it.

Evaluate an existing licensed artifact first. If none fits, a build-time Python training script may produce a small logistic regression from legally usable open data, with matches separated between train and validation. Check calibration and scenario behavior before release. The production page must never suggest goalkeeper or defender movement changes xG unless the model actually uses them.

**Learning note:** inference means evaluating a trained model on new input. Training is the separate process that derives its parameters. Running inference in the browser avoids a server round-trip but requires a small supported artifact and exactly matching feature calculations.
