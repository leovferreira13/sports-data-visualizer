import { loadModel, type ModelLoadResult } from "./model";

export const selectedArtifactId =
  "758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a";
export const selectedFileSha256 =
  "c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d";
export const selectedModelUrl = "/model/selected-model.json";

export function loadSelectedModel(value: unknown): ModelLoadResult {
  const result = loadModel(value);
  return result.status === "ready" &&
    result.model.artifactId !== selectedArtifactId
    ? { status: "invalid", reason: "artifact_contract" }
    : result;
}

/** Parse original bytes at runtime: Next's JSON module transform changes some doubles. */
export async function loadSelectedModelBytes(
  bytes: ArrayBuffer,
): Promise<ModelLoadResult> {
  try {
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    const checksum = Array.from(new Uint8Array(digest), (byte) =>
      byte.toString(16).padStart(2, "0"),
    ).join("");
    if (checksum !== selectedFileSha256)
      return { status: "invalid", reason: "artifact_contract" };
    return loadSelectedModel(
      JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)),
    );
  } catch {
    return { status: "invalid", reason: "artifact_schema" };
  }
}
