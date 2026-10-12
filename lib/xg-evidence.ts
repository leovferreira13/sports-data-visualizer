import "server-only";
import evidence from "../docs/reports/xg-final-first-run/app-evidence.json";
import distribution from "../docs/reports/xg-artifact-distribution-review.json";
import training from "../docs/reports/xg-training-first-run/evaluation.json";
import trainingManifest from "../docs/reports/xg-training-first-run/manifest.json";
import review from "../docs/reports/xg-final-review-record.json";
import { selectedArtifactId } from "./selected-model";

if (
  evidence.contract_version !== "xg-app-evidence/v1" ||
  evidence.selected_artifact_id !== selectedArtifactId ||
  evidence.evidence_id !== review.evidence_id ||
  evidence.training_run_id !== review.training_run_id ||
  trainingManifest.run_id !== evidence.training_run_id ||
  review.scientific_review !== "accepted_with_limitations"
) {
  throw new Error("Reviewed model/evidence identity mismatch");
}

export const xgEvidence = evidence;
export const scientificReview = review;
export const selectedTest = evidence.tables.final_test.find(
  (row) => row.role === "selected",
)!;
export const adverseConeSlice = selectedTest.slices.find(
  (row) =>
    row.feature === "defenders_in_cone_count" &&
    row.lower === 2 &&
    row.upper === 3,
)!;
if (!selectedTest || !adverseConeSlice)
  throw new Error("Required scientific evidence absent");

export const frozenConfiguration = evidence.tables.validation.find(
  (row) => row.id === "full_xgboost",
)!.configuration;

export const trainingPartitions = training.partitions;

export const selectedTreeCount = distribution.trees;
