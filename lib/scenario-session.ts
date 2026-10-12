import { getPreset, isPresetId, type PresetId } from "./presets";
import { isValidPosition, maxExtraPlayers, playerIds, maxRepresentedDefenders, type BaseDefenderId, type Scenario } from "./scenario";

export const scenarioSessionKey = "football-visualized-scenario";

export type SceneState = { presetId: PresetId; scenario: Scenario; migratedDefenderLimit?: boolean };

export function initialScene(): SceneState {
  return { presetId: "centralChance", scenario: getPreset("centralChance") };
}

export function parseScene(value: string | null): SceneState | null {
  if (!value) return null;
  try {
    const parsed: unknown = JSON.parse(value);
    if (typeof parsed !== "object" || parsed === null) return null;
    const snapshot = parsed as Record<string, unknown>;
    if ((snapshot.version !== 1 && snapshot.version !== 2 && snapshot.version !== 3) || !isPresetId(snapshot.presetId)) return null;
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
    if (extraAttackers.length > maxExtraPlayers.attacker || extraDefenders.length > (snapshot.version === 3 ? maxExtraPlayers.defender : 8)) return null;
    if (!extraAttackers.every(isValidPosition) || !extraDefenders.every(isValidPosition)) return null;
    const removed = snapshot.version === 3 ? record.removedBaseDefenders ?? [] : [];
    if (!Array.isArray(removed) || removed.some(id => id !== "defender1" && id !== "defender2")
      || new Set(removed).size !== removed.length) return null;
    const limit = maxRepresentedDefenders - (2 - removed.length);
    if (snapshot.version === 3 && extraDefenders.length > limit) return null;
    const migrated = snapshot.version !== 3 && extraDefenders.length > limit;
    return {
      ...(migrated ? { migratedDefenderLimit: true } : {}),
      presetId: snapshot.presetId,
      scenario: { shotType: record.shotType as Scenario["shotType"], players: players as Scenario["players"], extraAttackers, extraDefenders: extraDefenders.slice(0, limit),
        ...(removed.length ? { removedBaseDefenders: removed as BaseDefenderId[] } : {}) },
    };
  } catch {
    return null;
  }
}

export function serializeScene(state: SceneState): string {
  return JSON.stringify({ version: 3, presetId: state.presetId, scenario: state.scenario });
}
