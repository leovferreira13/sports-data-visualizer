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

  return match(languages, [...locales], defaultLocale) as Locale;
}
