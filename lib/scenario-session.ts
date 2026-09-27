import { getPreset, isPresetId, type PresetId } from "./presets";
import { isValidPosition, maxExtraPlayers, playerIds, type Scenario } from "./scenario";

export const scenarioSessionKey = "football-visualized-scenario";

export type SceneState = { presetId: PresetId; scenario: Scenario };

export function initialScene(): SceneState {
  return { presetId: "centralChance", scenario: getPreset("centralChance") };
}

export function parseScene(value: string | null): SceneState | null {
  if (!value) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    if (typeof parsed !== "object" || parsed === null) return null;
    const snapshot = parsed as Record<string, unknown>;
    if ((snapshot.version !== 1 && snapshot.version !== 2) || !isPresetId(snapshot.presetId)) return null;
    const scenario = snapshot.scenario;
    if (typeof scenario !== "object" || scenario === null) return null;
    const record = scenario as Record<string, unknown>;
    if (record.shotType !== getPreset(snapshot.presetId).shotType) return null;
    if (typeof record.players !== "object" || record.players === null) return null;
    const players = record.players as Record<string, unknown>;
    if (!playerIds.every((id) => isValidPosition(players[id]))) return null;
    const extraAttackers = snapshot.version === 1 ? [] : record.extraAttackers;
    const extraDefenders = snapshot.version === 1 ? [] : record.extraDefenders;
    if (!Array.isArray(extraAttackers) || !Array.isArray(extraDefenders)) return null;
    if (extraAttackers.length > maxExtraPlayers.attacker || extraDefenders.length > maxExtraPlayers.defender) return null;
    if (!extraAttackers.every(isValidPosition) || !extraDefenders.every(isValidPosition)) return null;
    return {
      presetId: snapshot.presetId,
      scenario: { shotType: record.shotType as Scenario["shotType"], players: players as Scenario["players"], extraAttackers, extraDefenders },
    };
  } catch {
    return null;
  }
}

export function serializeScene(state: SceneState): string {
  return JSON.stringify({ version: 2, ...state });
}
