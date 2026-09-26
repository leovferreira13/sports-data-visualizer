export const locales = ["en", "pt-BR"] as const;
export const localeRoutes = ["en", "br"] as const;

export type Locale = (typeof locales)[number];
export type LocaleRoute = (typeof localeRoutes)[number];

export const defaultLocale: Locale = "en";
export const localeCookieName = "football-visualized-locale";
export const localeCookieMaxAge = 60 * 60 * 24 * 365;

const routeToLocale: Record<LocaleRoute, Locale> = {
  en: "en",
  br: "pt-BR",
};

const localeToRoute: Record<Locale, LocaleRoute> = {
  en: "en",
  "pt-BR": "br",
};

export function isLocale(value: string | null | undefined): value is Locale {
  return locales.includes(value as Locale);
}

export function localeFromRoute(
  value: string | null | undefined,
): Locale | null {
  if (!localeRoutes.includes(value as LocaleRoute)) {
    return null;
  }

  return routeToLocale[value as LocaleRoute];
}

export function routeFromLocale(locale: Locale): LocaleRoute {
  return localeToRoute[locale];
}
