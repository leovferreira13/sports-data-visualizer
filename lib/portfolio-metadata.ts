import type { Metadata, MetadataRoute } from "next";

import { locales, routeFromLocale, type Locale } from "./i18n/config";
import { project } from "./project";

type MetaCopy = { title: string; description: string; imageAlt: string };

const ogLocales: Record<Locale, string> = {
  en: "en_US", "pt-BR": "pt_BR", nl: "nl_NL", es: "es_ES", de: "de_DE",
};

export function siteOrigin(value = process.env.SITE_URL): string | undefined {
  if (value === undefined) return undefined;
  const message = "SITE_URL must be a public HTTPS origin without credentials, port, path, query or fragment";
  let url: URL;
  try { url = new URL(value); } catch { throw new Error(message); }
  if (
    !/^https:\/\/[^/?#\\\s@]+\/?$/.test(value) || url.protocol !== "https:" || url.username || url.password ||
    url.port || url.pathname !== "/" || url.search || url.hash ||
    !url.hostname.includes(".") || url.hostname.endsWith(".localhost") ||
    url.hostname.endsWith(".local") || url.hostname.startsWith("[") ||
    /^\d+\.\d+\.\d+\.\d+$/.test(url.hostname)
  ) throw new Error(message);
  return url.origin;
}

export function languageUrls(origin: string): Record<string, string> {
  return Object.fromEntries([
    ...locales.map((locale) => [locale, `${origin}/${routeFromLocale(locale)}`]),
    ["x-default", `${origin}/en`],
  ]);
}

export function portfolioMetadata(locale: Locale, copy: MetaCopy, origin = siteOrigin()): Metadata {
  const canonical = origin ? `${origin}/${routeFromLocale(locale)}` : undefined;
  const image = { url: `${origin ?? ""}/portfolio/share.png`, width: 1200, height: 630, alt: copy.imageAlt };
  return {
    title: copy.title,
    description: copy.description,
    authors: [{ name: project.author, url: project.github }],
    robots: { index: Boolean(origin), follow: Boolean(origin) },
    ...(origin ? {
      metadataBase: new URL(origin),
      alternates: { canonical, languages: languageUrls(origin) },
    } : {}),
    openGraph: {
      type: "website", siteName: project.name, title: copy.title, description: copy.description,
      locale: ogLocales[locale], alternateLocale: locales.filter((item) => item !== locale).map((item) => ogLocales[item]),
      ...(canonical ? { url: canonical } : {}),
      // Next resolves relative OG images against localhost when metadataBase is absent.
      // Keep the asset usable locally, but emit share-image tags only with a public origin.
      ...(origin ? { images: [image] } : {}),
    },
    twitter: {
      card: "summary_large_image", title: copy.title, description: copy.description,
      ...(origin ? { images: [{ url: image.url, alt: image.alt }] } : {}),
    },
  };
}

export function portfolioRobots(origin = siteOrigin()): MetadataRoute.Robots {
  return origin
    ? { rules: { userAgent: "*", allow: "/" }, sitemap: `${origin}/sitemap.xml` }
    : { rules: { userAgent: "*", disallow: "/" } };
}

export function portfolioSitemap(origin = siteOrigin()): MetadataRoute.Sitemap {
  if (!origin) return [];
  return locales.map((locale) => ({
    url: `${origin}/${routeFromLocale(locale)}`,
    alternates: { languages: languageUrls(origin) },
  }));
}
