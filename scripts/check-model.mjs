import { createHash } from "node:crypto";
import { readFileSync, mkdirSync, copyFileSync } from "node:fs";

const hash = (path) =>
  createHash("sha256").update(readFileSync(path)).digest("hex");
const read = (path) => JSON.parse(readFileSync(path, "utf8"));
const artifact = read("model/selected-model.json");
const rights = read("docs/reports/xg-artifact-distribution-review.json");
const evidence = read("docs/reports/xg-final-first-run/app-evidence.json");
const trainingManifest = read(
  "docs/reports/xg-training-first-run/manifest.json",
);
const scientific = read("docs/reports/xg-final-review-record.json");
if (
  hash("model/selected-model.json") !== rights.file_sha256 ||
  rights.artifact_id !== artifact.artifact_id ||
  artifact.artifact_id !== evidence.selected_artifact_id ||
  artifact.feature_contract_sha256 !== hash("model/feature-contract.json") ||
  hash("docs/reports/xg-final-first-run/app-evidence.json") !==
    "4940016cda64e1d639f11cd592b9fb32e1b481aedd79350d5ddbdf574c068c96" ||
  hash("docs/reports/xg-training-first-run/evaluation.json") !==
    trainingManifest.outputs["evaluation.json"] ||
  trainingManifest.run_id !== evidence.training_run_id ||
  evidence.evidence_id !== scientific.evidence_id ||
  evidence.training_run_id !== scientific.training_run_id ||
  evidence.contract_version !== "xg-app-evidence/v1" ||
  scientific.scientific_review !== "accepted_with_limitations"
) {
  throw new Error(
    "Frozen model / immutable aggregate / reviewed provenance mismatch",
  );
}
console.log(
  "PASS: exact reviewed parameter bytes, feature contract and aggregate evidence",
);

// Serve original bytes; importing numeric JSON through Turbopack changes some doubles.
mkdirSync("public/model", { recursive: true });
copyFileSync("model/selected-model.json", "public/model/selected-model.json");
