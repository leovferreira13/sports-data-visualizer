import "server-only";

import type { Locale } from "./config";

export type Dictionary = typeof import("../../locales/en.json");

const dictionaries: Record<Locale, () => Promise<Dictionary>> = {
  en: () => import("@/locales/en.json").then((module) => module.default),
  "pt-BR": () =>
    import("@/locales/pt-BR.json").then((module) => module.default),
  nl: () => import("@/locales/nl.json").then((module) => module.default),
  es: () => import("@/locales/es.json").then((module) => module.default),
  de: () => import("@/locales/de.json").then((module) => module.default),
};

export function getDictionary(locale: Locale) {
  return dictionaries[locale]();
}
