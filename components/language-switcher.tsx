"use client";

import { useRouter } from "next/navigation";
import type { ChangeEvent } from "react";

import {
  isLocale,
  localeCookieMaxAge,
  localeCookieName,
  routeFromLocale,
  type Locale,
} from "@/lib/i18n/config";

type LanguageSwitcherProps = {
  currentLocale: Locale;
  label: string;
  englishLabel: string;
  portugueseLabel: string;
};

export function LanguageSwitcher({
  currentLocale,
  label,
  englishLabel,
  portugueseLabel,
}: LanguageSwitcherProps) {
  const router = useRouter();

  function changeLocale(event: ChangeEvent<HTMLSelectElement>) {
    const nextLocale = event.target.value;

    if (!isLocale(nextLocale) || nextLocale === currentLocale) {
      return;
    }

    document.cookie = [
      `${localeCookieName}=${encodeURIComponent(nextLocale)}`,
      "Path=/",
      `Max-Age=${localeCookieMaxAge}`,
      "SameSite=Lax",
    ].join("; ");

    const segments = window.location.pathname.split("/");
    segments[1] = routeFromLocale(nextLocale);

    const target =
      segments.join("/") + window.location.search + window.location.hash;

    router.replace(target);
  }

  return (
    <label className="language-switcher">
      <span>{label}</span>
      <select value={currentLocale} onChange={changeLocale}>
        <option value="en">🇺🇸 {englishLabel}</option>
        <option value="pt-BR">🇧🇷 {portugueseLabel}</option>
      </select>
    </label>
  );
}
