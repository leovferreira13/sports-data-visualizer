import { match } from "@formatjs/intl-localematcher";
import Negotiator from "negotiator";

import { defaultLocale, isLocale, locales, type Locale } from "./config";

export function resolveLocale(
  savedLocale: string | undefined,
  acceptLanguage: string | null,
): Locale {
  if (isLocale(savedLocale)) {
    return savedLocale;
  }

  if (!acceptLanguage) {
    return defaultLocale;
  }

  const languages = new Negotiator({
    headers: { "accept-language": acceptLanguage },
  }).languages();

  // Wildcards are valid HTTP preferences but are not BCP 47 language tags.
  try {
    return match(languages.filter((language) => language !== "*"), [...locales], defaultLocale) as Locale;
  } catch (error) {
    if (error instanceof RangeError) return defaultLocale;
    throw error;
  }
}
