import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { languageOptions, locales, localeRoutes, localeFromRoute, routeFromLocale, isLocale } from "./config";
import { resolveLocale } from "./resolve-locale";
import { probabilityLabels } from "../insights";

function shape(value: unknown, path = ""): string[] {
  if (typeof value === "string") {
    expect(value.trim(), path).not.toBe("");
    return [`${path}:string`];
  }
  if (Array.isArray(value)) return [`${path}:array:${value.length}`, ...value.flatMap((v, i) => shape(v, `${path}[${i}]`))];
  expect(value, path).not.toBeNull();
  expect(typeof value, path).toBe("object");
  return Object.entries(value as Record<string, unknown>).flatMap(([key, v]) => shape(v, `${path}.${key}`)).sort();
}

describe("five-language contract", () => {
  it("has a complete, nonempty dictionary for every supported locale", () => {
    const reference = shape(JSON.parse(readFileSync("locales/en.json", "utf8")));
    for (const locale of locales) {
      expect(shape(JSON.parse(readFileSync(`locales/${locale}.json`, "utf8")))).toEqual(reference);
    }
    expect(languageOptions.map((x) => x.locale)).toEqual([...locales]);
    expect(new Set(languageOptions.map((x) => x.label)).size).toBe(5);
  });
  it("round-trips routes while keeping br separate from pt-BR", () => {
    for (const route of localeRoutes) {
      const locale = localeFromRoute(route)!;
      expect(isLocale(locale)).toBe(true);
      expect(routeFromLocale(locale)).toBe(route);
    }
    for (const invalid of ["fr", "pt-BR", "de-DE", "", undefined]) expect(localeFromRoute(invalid)).toBeNull();
    expect(localeFromRoute("br")).toBe("pt-BR");
  });
  it.each([
    ["pt-BR,pt;q=0.9", "pt-BR"], ["en-US,en;q=0.8", "en"],
    ["nl-NL,nl;q=0.8", "nl"], ["nl-BE", "nl"], ["es-ES", "es"],
    ["es-MX", "es"], ["de-DE", "de"], ["de-AT", "de"],
    ["de;q=0.3,es;q=0.9,en;q=0.5", "es"], ["fr-FR", "en"],
    [null, "en"], ["", "en"], ["*", "en"], ["not_a_tag", "en"],
    ["*;q=0.1,de;q=0.9", "de"], ["de;q=0", "en"],
  ])("resolves %s to %s", (header, expected) => {
    expect(resolveLocale(undefined, header)).toBe(expected);
    expect(resolveLocale("invalid", header)).toBe(expected);
  });
  it("gives every valid saved preference precedence over the browser", () => {
    for (const locale of locales) expect(resolveLocale(locale, "fr-FR,es;q=0.9")).toBe(locale);
  });
  it("formats the same probability without changing numeric values", () => {
    for (const locale of locales) {
      const value = 0.76;
      expect(probabilityLabels(value, locale)).toEqual({
        xg: new Intl.NumberFormat(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value),
        percent: new Intl.NumberFormat(locale, { style: "percent", minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(value),
      });
    }
  });
});
