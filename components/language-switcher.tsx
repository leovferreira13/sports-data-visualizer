"use client";

import { useRouter } from "next/navigation";
import { useRef, useState, useTransition, type ChangeEvent } from "react";

import {
  isLocale,
  languageOptions,
  localeCookieMaxAge,
  localeCookieName,
  routeFromLocale,
  type Locale,
} from "@/lib/i18n/config";

type LanguageSwitcherProps = {
  currentLocale: Locale;
  label: string;
  loadingLabel: string;
};

export function LanguageSwitcher({
  currentLocale,
  label,
  loadingLabel,
}: LanguageSwitcherProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  const [requestedLocale, setRequestedLocale] = useState(currentLocale);
  const prefetched = useRef(new Set<string>());

  function targetFor(locale: Locale) {
    const segments = window.location.pathname.split("/");
    segments[1] = routeFromLocale(locale);
    return segments.join("/") + window.location.search + window.location.hash;
  }

  function warmLanguages() {
    for (const { locale } of languageOptions) {
      if (locale === currentLocale) continue;
      const target = targetFor(locale);
      if (prefetched.current.has(target)) continue;
      prefetched.current.add(target);
      router.prefetch(target);
    }
  }

  function changeLocale(event: ChangeEvent<HTMLSelectElement>) {
    const nextLocale = event.target.value;

    if (isPending || !isLocale(nextLocale) || nextLocale === currentLocale) {
      return;
    }

    document.cookie = [
      `${localeCookieName}=${encodeURIComponent(nextLocale)}`,
      "Path=/",
      `Max-Age=${localeCookieMaxAge}`,
      "SameSite=Lax",
    ].join("; ");

    setRequestedLocale(nextLocale);
    startTransition(() => router.replace(targetFor(nextLocale), { scroll: false }));
  }

  return (
    <div className="language-switcher">
      <label aria-busy={isPending}>
        <span>{label}</span>
        <select
          value={isPending ? requestedLocale : currentLocale}
          onChange={changeLocale}
          onFocus={warmLanguages}
          onPointerEnter={warmLanguages}
          disabled={isPending}
        >
          {languageOptions.map(({ locale, label, flag }) => (
            <option key={locale} value={locale}>{flag} {label}</option>
          ))}
        </select>
      </label>
      {isPending && (
        <div className="locale-loading" role="status" aria-live="polite" aria-atomic="true">
          <div className="locale-loading-card">
            <span className="locale-loading-spinner" aria-hidden="true" />
            <span>{loadingLabel}</span>
          </div>
        </div>
      )}
    </div>
  );
}
