import { readFileSync } from "node:fs";

import { monotonicArtifactId } from "./dev-compare";
import { loadModel } from "./model";

export type CompareEnv = {
  XG_COMPARE?: string;
  XG_CANDIDATE_MODEL?: string;
};

export type CandidateLoad =
  | { status: "disabled" }
  | { status: "missing-path" }
  | { status: "unreadable" }
  | { status: "invalid" }
  | { status: "ready"; text: string };

/** The candidate path comes only from the environment, never from a request URL. */
export function loadCompareCandidate(
  env: CompareEnv,
  read: (path: string) => string = (path) => readFileSync(path, "utf8"),
): CandidateLoad {
  if (env.XG_COMPARE !== "1") return { status: "disabled" };
  const path = env.XG_CANDIDATE_MODEL;
  if (!path) return { status: "missing-path" };
  let text: string;
  try {
    text = read(path);
  } catch {
    return { status: "unreadable" };
  }
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    return { status: "invalid" };
  }
  const loaded = loadModel(parsed);
  if (loaded.status !== "ready" || loaded.model.artifactId !== monotonicArtifactId) {
    return { status: "invalid" };
  }
  return { status: "ready", text };
}
