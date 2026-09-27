import "server-only";

import type { Locale } from "./config";

export type Dictionary = {
  meta: { title: string; description: string };
  brand: { name: string; tagline: string };
  language: { label: string; english: string; portuguese: string };
  playground: {
    eyebrow: string;
    title: string;
    description: string;
    status: string;
    pitchDescription: string;
    keyboardHint: string;
    distance: string;
    angle: string;
    meters: string;
    presetLabel: string;
    reset: string;
    forward: string;
    sideways: string;
    players: { shooter: string; goalkeeper: string; defender1: string; defender2: string };
    playerGlyphs: { shooter: string; goalkeeper: string; defender1: string; defender2: string };
    presets: {
      centralChance: string;
      penalty: string;
      oneOnOne: string;
      tightAngle: string;
      longShot: string;
      crowdedBox: string;
    };
  };
};

const dictionaries: Record<Locale, () => Promise<Dictionary>> = {
  en: () => import("@/locales/en.json").then((module) => module.default),
  "pt-BR": () =>
    import("@/locales/pt-BR.json").then((module) => module.default),
};

export function getDictionary(locale: Locale) {
  return dictionaries[locale]();
}
