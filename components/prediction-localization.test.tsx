import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { PredictionPanel } from "./prediction-panel";
import { locales } from "../lib/i18n/config";
import type { Dictionary } from "../lib/i18n/dictionaries";
import { getPreset } from "../lib/presets";
import type { PredictionResult } from "../lib/predict";

describe("localized prediction failure states", () => {
  it.each(locales)("renders loading, unavailable and unsupported messages in %s", (locale) => {
    const dictionary: Dictionary = JSON.parse(readFileSync(`locales/${locale}.json`, "utf8"));
    const copy = dictionary.playground.results;
    const states: [PredictionResult, boolean, string][] = [
      [{ status: "unavailable", reason: "missing_model" }, true, copy.loading],
      [{ status: "unavailable", reason: "missing_model" }, false, copy.unavailable],
      [{ status: "unsupported", reason: "unsupported_shot_type" }, false, copy.unsupported],
    ];
    for (const [result, loading, message] of states) {
      const html = renderToStaticMarkup(createElement(PredictionPanel, { locale, copy, scenario: getPreset("centralChance"), result, loading }));
      expect(html).toContain(message);
      expect(html).not.toContain('data-testid="xg"');
    }
  });
});
