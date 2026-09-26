import type { Metadata } from "next";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { LanguageSwitcher } from "@/components/language-switcher";
import { isLocale, locales } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";

import "./globals.css";

type LocaleLayoutProps = {
  children: ReactNode;
  params: Promise<{ lang: string }>;
};

export const dynamicParams = false;

export function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export async function generateMetadata({
  params,
}: Omit<LocaleLayoutProps, "children">): Promise<Metadata> {
  const { lang } = await params;

  if (!isLocale(lang)) {
    return {};
  }

  const dictionary = await getDictionary(lang);

  return {
    title: dictionary.meta.title,
    description: dictionary.meta.description,
  };
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { lang } = await params;

  if (!isLocale(lang)) {
    notFound();
  }

  const dictionary = await getDictionary(lang);

  return (
    <html lang={lang}>
      <body>
        <div className="site-shell">
          <header className="site-header">
            <div className="brand">
              <strong>{dictionary.brand.name}</strong>
              <span>{dictionary.brand.tagline}</span>
            </div>

            <LanguageSwitcher
              currentLocale={lang}
              label={dictionary.language.label}
              englishLabel={dictionary.language.english}
              portugueseLabel={dictionary.language.portuguese}
            />
          </header>

          {children}
        </div>
      </body>
    </html>
  );
}
