import { FIELD, type BaseScenario, type Scenario } from "./scenario";

export const presetIds = [
  "centralChance",
  "penalty",
  "oneOnOne",
  "tightAngle",
  "longShot",
  "crowdedBox",
] as const;
export type PresetId = (typeof presetIds)[number];

const presets: Record<PresetId, BaseScenario> = {
  centralChance: {
    shotType: "open-play",
    players: {
      shooter: { x: 84, y: FIELD.centerY },
      goalkeeper: { x: 102, y: FIELD.centerY },
      defender1: { x: 93, y: FIELD.centerY - 3 },
      defender2: { x: 93, y: FIELD.centerY + 3 },
    },
  },
  penalty: {
    shotType: "penalty",
    players: {
      shooter: { x: FIELD.length - 11, y: 34 },
      goalkeeper: { x: 102.5, y: 34 },
      defender1: { x: 83, y: 23 },
      defender2: { x: 83, y: 45 },
    },
  },
  oneOnOne: {
    shotType: "open-play",
    players: {
      shooter: { x: 89, y: 34 },
      goalkeeper: { x: 100, y: 35 },
      defender1: { x: 79, y: 24 },
      defender2: { x: 78, y: 46 },
    },
  },
  tightAngle: {
    shotType: "open-play",
    players: {
      shooter: { x: 98, y: 52 },
      goalkeeper: { x: 102, y: 36 },
      defender1: { x: 96, y: 45 },
      defender2: { x: 88, y: 48 },
    },
  },
  longShot: {
    shotType: "open-play",
    players: {
      shooter: { x: 65, y: 30 },
      goalkeeper: { x: 102, y: 34 },
      defender1: { x: 83, y: 30 },
      defender2: { x: 85, y: 42 },
    },
  },
  crowdedBox: {
    shotType: "open-play",
    players: {
      shooter: { x: 94, y: 30 },
      goalkeeper: { x: 102, y: 34 },
      defender1: { x: 99, y: 31 },
      defender2: { x: 97, y: 35 },
    },
  },
};

export function isPresetId(value: unknown): value is PresetId {
  return typeof value === "string" && presetIds.some((id) => id === value);
}

export function getPreset(id: PresetId): Scenario {
  return {
    shotType: presets[id].shotType,
    extraAttackers: [],
    extraDefenders: [],
    players: {
      shooter: { ...presets[id].players.shooter },
      goalkeeper: { ...presets[id].players.goalkeeper },
      defender1: { ...presets[id].players.defender1 },
      defender2: { ...presets[id].players.defender2 },
    },
  };
}
