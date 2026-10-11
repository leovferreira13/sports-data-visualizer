import { describe, expect, it } from "vitest";
import fixtures from "../tests/fixtures/training-presets.json";
import { getPreset, presetIds, type PresetId } from "./presets";

describe("offline training scene definitions", () => {
  it("checks every synthetic training preset against the live browser preset", () => {
    expect(fixtures.map(f => f.name)).toEqual([...presetIds]);
    for (const fixture of fixtures) {
      const preset = getPreset(fixture.name as PresetId);
      expect(fixture.scene.shot_type).toBe(preset.shotType);
      expect(fixture.scene.shooter).toEqual(preset.players.shooter);
      expect(fixture.scene.goalkeepers).toEqual([preset.players.goalkeeper]);
      expect(fixture.scene.defenders).toEqual([preset.players.defender1, preset.players.defender2]);
    }
  });
});
