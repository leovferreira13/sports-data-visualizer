import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import evidence from "../docs/reports/xg-final-first-run/app-evidence.json";
import review from "../docs/reports/xg-artifact-distribution-review.json";
import envelope from "../model/selected-model.json";
import { extractScenarioFeatures } from "./features";
import { compareScenes, probabilityLabels } from "./insights";
import { predictScenario } from "./predict";
import { getPreset, presetIds } from "./presets";
import { loadSelectedModel, loadSelectedModelBytes } from "./selected-model";
import { parseScene, serializeScene } from "./scenario-session";
import {
  addPlayer,
  defenderCount,
  movePlayer,
  removePlayer,
  representedPlayerIds,
} from "./scenario";

const selectedModel = loadSelectedModel(envelope);
if (selectedModel.status !== "ready")
  throw new Error("Reviewed model unavailable");
const model = selectedModel.model;

describe("actual reviewed model and evidence", () => {
  it("pins original bytes, reviewed identity and original preset outputs", () => {
    expect(
      createHash("sha256")
        .update(readFileSync("model/selected-model.json"))
        .digest("hex"),
    ).toBe(review.file_sha256);
    expect(envelope.artifact_id).toBe(review.artifact_id);
    expect(model.artifactId).toBe(evidence.selected_artifact_id);
    expect(
      createHash("sha256")
        .update(
          readFileSync("docs/reports/xg-final-first-run/app-evidence.json"),
        )
        .digest("hex"),
    ).toBe("4940016cda64e1d639f11cd592b9fb32e1b481aedd79350d5ddbdf574c068c96");
    expect(
      loadSelectedModel({ ...envelope, artifact_id: "a".repeat(64) }).status,
    ).toBe("invalid");
    for (const id of presetIds) {
      const result = predictScenario(getPreset(id), model);
      const diagnostic = evidence.scene_audit.diagnostics.find(
        (d) => d.scene === id,
      )!;
      expect(result.status).toBe("ok");
      if (result.status === "ok")
        expect(
          Math.abs(result.probability - diagnostic.probability!),
        ).toBeLessThanOrEqual(1e-7);
    }
  });
  it("verifies the original downloadable bytes before parsing, rejecting changes", async () => {
    const bytes = readFileSync("model/selected-model.json");
    const original = await loadSelectedModelBytes(
      Uint8Array.from(bytes).buffer,
    );
    expect(original.status).toBe("ready");
    const changed = Buffer.concat([bytes, Buffer.from(" ")]);
    expect(
      await loadSelectedModelBytes(Uint8Array.from(changed).buffer),
    ).toEqual({ status: "invalid", reason: "artifact_contract" });
  });
});

describe("deliberate defender editing and snapshots", () => {
  it("adds every penalty participant outside the area even after editing and restoration", () => {
    let scene = movePlayer(getPreset("penalty"), "shooter", { x: 100, y: 34 });
    for (let i = 0; i < 9; i++) scene = addPlayer(scene, "attacker");
    scene = addPlayer(scene, "defender");
    for (const p of [...scene.extraAttackers, ...scene.extraDefenders]) {
      expect(p.x + 1.4).toBeLessThan(105 - 16.5);
    }
    scene = movePlayer(scene, "defender1", { x: 100, y: 34 });
    scene = addPlayer(removePlayer(scene, "defender1"), "defender");
    expect(scene.players.defender1.x + 1.4).toBeLessThan(105 - 16.5);
    expect(defenderCount(scene)).toBe(3);
  });
  it("supports zero through three defenders without changing the feature domain", () => {
    let scene = getPreset("centralChance");
    scene = removePlayer(removePlayer(scene, "defender1"), "defender2");
    expect(representedPlayerIds(scene)).toEqual(["shooter", "goalkeeper"]);
    const empty = predictScenario(scene, model);
    expect(empty).toMatchObject({
      status: "ok",
      warnings: [
        "represented_scene_not_empirical_support",
        "zero_defender_support_unestablished",
      ],
    });
    for (const count of [1, 2, 3]) {
      scene = addPlayer(scene, "defender");
      expect(defenderCount(scene)).toBe(count);
      const features = extractScenarioFeatures(scene);
      expect(features.status).toBe("ok");
      if (features.status === "ok")
        expect(features.features.visible_defender_count).toBe(count);
    }
    expect(addPlayer(scene, "defender")).toBe(scene);
    expect(removePlayer(scene, "shooter")).toBe(scene);
    expect(removePlayer(scene, "goalkeeper")).toBe(scene);
    expect(
      parseScene(serializeScene({ presetId: "centralChance", scenario: scene }))
        ?.scenario,
    ).toEqual(scene);
  });
  it("rejects malformed exclusions and missing positions rather than imputing", () => {
    const base = getPreset("centralChance");
    for (const removedBaseDefenders of [
      ["goalkeeper"],
      ["defender1", "defender1"],
      "defender1",
    ]) {
      expect(
        extractScenarioFeatures({ ...base, removedBaseDefenders }).status,
      ).toBe("unsupported");
      expect(
        parseScene(
          JSON.stringify({
            version: 3,
            presetId: "centralChance",
            scenario: { ...base, removedBaseDefenders },
          }),
        ),
      ).toBeNull();
    }
    const bad = {
      ...base,
      players: { ...base.players, defender1: undefined },
      removedBaseDefenders: ["defender1"],
    };
    expect(extractScenarioFeatures(bad).status).toBe("unsupported");
  });
  it("migrates oversized v2 while preserving coordinates and rejects oversized v3", () => {
    const scene = getPreset("longShot");
    scene.extraDefenders = [
      { x: 80, y: 20 },
      { x: 81, y: 21 },
      { x: 82, y: 22 },
    ];
    const snapshot = { version: 2, presetId: "longShot", scenario: scene };
    const restored = parseScene(JSON.stringify(snapshot))!;
    expect(restored.migratedDefenderLimit).toBe(true);
    expect(restored.scenario.players).toEqual(scene.players);
    expect(restored.scenario.extraDefenders).toEqual([scene.extraDefenders[0]]);
    expect(
      parseScene(serializeScene(restored))?.migratedDefenderLimit,
    ).toBeUndefined();
    expect(parseScene(JSON.stringify({ ...snapshot, version: 3 }))).toBeNull();
  });
});

describe("honest comparisons", () => {
  it("separates plateaus, omitted attackers, penalties and errors", () => {
    const before = getPreset("centralChance"),
      a = predictScenario(before, model);
    const tiny = movePlayer(before, "shooter", { x: 84 + 1e-10, y: 34 });
    expect(
      compareScenes(before, tiny, a, predictScenario(tiny, model))?.kind,
    ).toBe("plateau");
    const attacker = addPlayer(before, "attacker");
    expect(
      compareScenes(before, attacker, a, predictScenario(attacker, model))
        ?.kind,
    ).toBe("omitted");
    expect(
      compareScenes(before, tiny, a, {
        status: "unavailable",
        reason: "missing_model",
      }),
    ).toBeNull();
    const penalty = getPreset("penalty"),
      p = predictScenario(penalty);
    expect(
      compareScenes(penalty, removePlayer(penalty, "defender1"), p, p)?.kind,
    ).toBe("convention");
    expect(compareScenes(before, penalty, a, p)).toBeNull();
  });
  it("distinguishes an actual sub-display delta and localizes small values", () => {
    const scene = getPreset("centralChance"),
      a = predictScenario(scene, model);
    if (a.status !== "ok" || a.source !== "learned-model")
      throw new Error("Invalid test fixture");
    const result = compareScenes(scene, scene, a, {
      ...a,
      probability: a.probability + 0.00001,
    });
    expect(result?.kind).toBe("below-resolution");
    expect(result?.delta).toBeGreaterThan(0);
    expect(probabilityLabels(0.00001, "pt-BR").xg).toMatch(/^< /);
    expect(probabilityLabels(0.2, "pt-BR")).toEqual({
      xg: "0,20",
      percent: "20,0%",
    });
  });
});
