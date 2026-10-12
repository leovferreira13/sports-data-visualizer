export const locales = ["en", "pt-BR", "nl", "es", "de"] as const;
export const localeRoutes = ["en", "br", "nl", "es", "de"] as const;

export type Locale = (typeof locales)[number];
export type LocaleRoute = (typeof localeRoutes)[number];

export const languageOptions: readonly { locale: Locale; label: string; flag: string }[] = [
  { locale: "en", label: "English", flag: "🇺🇸" },
  { locale: "pt-BR", label: "Português (Brasil)", flag: "🇧🇷" },
  { locale: "nl", label: "Nederlands", flag: "🇳🇱" },
  { locale: "es", label: "Español", flag: "🇪🇸" },
  { locale: "de", label: "Deutsch", flag: "🇩🇪" },
];

export const defaultLocale: Locale = "en";
export const localeCookieName = "football-visualized-locale";
export const localeCookieMaxAge = 60 * 60 * 24 * 365;

const routeToLocale: Record<LocaleRoute, Locale> = {
  en: "en",
  br: "pt-BR",
  nl: "nl",
  es: "es",
  de: "de",
};

const localeToRoute: Record<Locale, LocaleRoute> = {
  en: "en",
  "pt-BR": "br",
  nl: "nl",
  es: "es",
  de: "de",
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
