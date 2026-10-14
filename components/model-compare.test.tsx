import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { ModelCompare, nudgePlayer } from "./model-compare";
import { monotonicArtifactId } from "../lib/dev-compare";
import { loadCompareCandidate } from "../lib/dev-compare-server";
import { loadModel } from "../lib/model";
import { predictScenario } from "../lib/predict";
import { getPreset } from "../lib/presets";
import { loadSelectedModel, selectedArtifactId } from "../lib/selected-model";
import { playerPosition } from "../lib/scenario";

const currentText = readFileSync("model/selected-model.json", "utf8");

function candidateText() {
  const envelope = JSON.parse(currentText) as {
    model_version: string;
    artifact_id: string;
    parameters: { trees: { leaf?: number }[][] };
  };
  envelope.model_version = "full_monotonic_xgboost";
  envelope.artifact_id = monotonicArtifactId;
  envelope.parameters.trees = [[{ leaf: 1.2 }]];
  return JSON.stringify(envelope);
}

describe("local monotonic comparison", () => {
  it("renders one scene against the published artifact and the monotonic artifact", () => {
    const html = renderToStaticMarkup(
      createElement(ModelCompare, { currentText, candidateText: candidateText() }),
    );
    const scene = getPreset("centralChance");
    const current = loadSelectedModel(JSON.parse(currentText));
    const candidate = loadModel(JSON.parse(candidateText()));
    expect(current.status).toBe("ready");
    expect(candidate.status).toBe("ready");
    if (current.status !== "ready" || candidate.status !== "ready") return;
    const currentLabels = predictScenario(scene, current.model);
    const candidateLabels = predictScenario(scene, candidate.model);
    expect(currentLabels.status).toBe("ok");
    expect(candidateLabels.status).toBe("ok");
    if (currentLabels.status !== "ok" || candidateLabels.status !== "ok") return;
    expect(currentLabels.probability).not.toBe(candidateLabels.probability);
    expect(html).toContain(selectedArtifactId);
    expect(html).toContain(monotonicArtifactId);
    expect(html).toContain('data-testid="compare-current-xg"');
    expect(html).toContain('data-testid="compare-candidate-xg"');
    expect(html).toContain("Use the arrow keys");
    expect(html.match(/role="button"/g)?.length).toBeGreaterThan(2);
  });

  it("moves the shooter toward the goal with the up arrow and keeps one scene", () => {
    const scene = getPreset("centralChance");
    const moved = nudgePlayer(scene, "shooter", "ArrowUp", true);
    expect(moved).not.toBeNull();
    if (!moved) return;
    expect(playerPosition(moved, "shooter").x).toBe(playerPosition(scene, "shooter").x + 5);
    expect(playerPosition(moved, "goalkeeper")).toEqual(playerPosition(scene, "goalkeeper"));
    const current = loadSelectedModel(JSON.parse(currentText));
    const candidate = loadModel(JSON.parse(candidateText()));
    if (current.status !== "ready" || candidate.status !== "ready") throw new Error("models");
    const before = [
      predictScenario(scene, current.model),
      predictScenario(scene, candidate.model),
    ];
    const after = [
      predictScenario(moved, current.model),
      predictScenario(moved, candidate.model),
    ];
    expect(before.every((result) => result.status === "ok")).toBe(true);
    expect(after.every((result) => result.status === "ok")).toBe(true);
    expect(nudgePlayer(scene, "shooter", "Enter", false)).toBeNull();
  });

  it("loads a candidate only from XG_CANDIDATE_MODEL when comparison is enabled", () => {
    const text = candidateText();
    expect(loadCompareCandidate({}).status).toBe("disabled");
    expect(loadCompareCandidate({ XG_COMPARE: "1" }).status).toBe("missing-path");
    expect(
      loadCompareCandidate({ XG_COMPARE: "1", XG_CANDIDATE_MODEL: "/tmp/missing.json" }, () => {
        throw new Error("missing");
      }).status,
    ).toBe("unreadable");
    const ready = loadCompareCandidate(
      { XG_COMPARE: "1", XG_CANDIDATE_MODEL: "/private/candidate-model.json" },
      () => text,
    );
    expect(ready.status).toBe("ready");
    const wrong = JSON.parse(text) as { artifact_id: string };
    wrong.artifact_id = "a".repeat(64);
    expect(
      loadCompareCandidate(
        { XG_COMPARE: "1", XG_CANDIDATE_MODEL: "/private/candidate-model.json" },
        () => JSON.stringify(wrong),
      ).status,
    ).toBe("invalid");
  });
});
