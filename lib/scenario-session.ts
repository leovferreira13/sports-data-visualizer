import { getPreset, isPresetId, type PresetId } from "./presets";
import { isValidPosition, playerIds, type Scenario } from "./scenario";

export const scenarioSessionKey = "football-visualized-scenario";

export type SceneState = { presetId: PresetId; scenario: Scenario };

export function initialScene(): SceneState {
  return { presetId: "oneOnOne", scenario: getPreset("oneOnOne") };
}

export function parseScene(value: string | null): SceneState | null {
  if (!value) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    if (typeof parsed !== "object" || parsed === null) return null;
    const snapshot = parsed as Record<string, unknown>;
    if (snapshot.version !== 1 || !isPresetId(snapshot.presetId)) return null;
    const scenario = snapshot.scenario;
    if (typeof scenario !== "object" || scenario === null) return null;
    const record = scenario as Record<string, unknown>;
    if (record.shotType !== getPreset(snapshot.presetId).shotType) return null;
    if (typeof record.players !== "object" || record.players === null) return null;
    const players = record.players as Record<string, unknown>;
    if (!playerIds.every((id) => isValidPosition(players[id]))) return null;
    return { presetId: snapshot.presetId, scenario: scenario as Scenario };
  } catch {
    return null;
  }
}

export function serializeScene(state: SceneState): string {
  return JSON.stringify({ version: 1, ...state });
}
