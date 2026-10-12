import type { Metadata } from "next";
import Image from "next/image";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { SectionNavigation } from "@/components/section-navigation";
import { LanguageSwitcher } from "@/components/language-switcher";
import {
  localeFromRoute,
  localeRoutes,
} from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";

import "./globals.css";

type LocaleLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export const dynamicParams = false;

export function generateStaticParams() {
  return localeRoutes.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: Omit<LocaleLayoutProps, "children">): Promise<Metadata> {
  const { locale: routeLocale } = await params;
  const locale = localeFromRoute(routeLocale);

  if (!locale) {
    return {};
  }

  const dictionary = await getDictionary(locale);

  return {
    title: dictionary.meta.title,
    description: dictionary.meta.description,
  };
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { locale: routeLocale } = await params;
  const locale = localeFromRoute(routeLocale);

  if (!locale) {
    notFound();
  }

  const dictionary = await getDictionary(locale);

  return (
    <html lang={locale}>
      <body>
        <div className="site-shell">
          <header className="site-header">
            <div className="brand">
              <strong>{dictionary.brand.name}</strong>
              <span>{dictionary.brand.tagline}</span>
            </div>

            <LanguageSwitcher
              currentLocale={locale}
              label={dictionary.language.label}
              englishLabel={dictionary.language.english}
              portugueseLabel={dictionary.language.portuguese}
            />
          </header>

          <SectionNavigation route={routeLocale} copy={dictionary.navigation} />
          {children}

          <footer className="site-footer">
            <a
              className="data-source-logo"
              href="https://github.com/hudl/open-data"
              aria-label={dictionary.attribution.sourceLink}
            >
              <Image
                src="/branding/hudl-statsbomb-logo-reversed.png"
                width={800}
                height={122}
                alt={dictionary.attribution.logoAlt}
              />
            </a>
            <p>{dictionary.attribution.disclaimer}</p>
          </footer>
        </div>
      </body>
    </html>
  );
}
