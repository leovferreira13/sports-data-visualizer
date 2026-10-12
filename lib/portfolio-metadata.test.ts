import { afterEach, describe, expect, it, vi } from "vitest";
import { locales, routeFromLocale } from "./i18n/config";
import { portfolioMetadata, portfolioRobots, portfolioSitemap, siteOrigin } from "./portfolio-metadata";

const origin = "https://portfolio.example.com";
const copy = { title: "xG playground", description: "Explore a scene", imageAlt: "Illustrative scene" };

afterEach(() => vi.unstubAllEnvs());

describe("portfolio deployment contract", () => {
  it("normalizes a public HTTPS origin and rejects unusable values", () => {
    expect(siteOrigin(`${origin}/`)).toBe(origin);
    for (const value of ["", "not a URL", "http://example.com", "https://localhost", "https://127.0.0.1", "https://[::1]", "https://test.local", "https://a.localhost", `${origin}/en`, `${origin}/..`, `${origin}/en/../`, `${origin}?a=1`, `${origin}#a`, "https://user:password@example.com", "https://@example.com", "https://example.com:444", ` ${origin}`, "https://exam\nple.com"]) {
      expect(() => siteOrigin(value), value).toThrow("SITE_URL");
    }
  });

  it("keeps an unconfigured build non-indexable without guessed sharing URLs", () => {
    vi.stubEnv("SITE_URL", undefined);
    expect(siteOrigin()).toBeUndefined();
    const metadata = portfolioMetadata("en", copy);
    expect(metadata.alternates).toBeUndefined();
    expect(metadata.metadataBase).toBeUndefined();
    expect(metadata.robots).toEqual({ index: false, follow: false });
    expect(metadata.openGraph).not.toHaveProperty("images");
    expect(metadata.openGraph).not.toHaveProperty("url");
    expect(metadata.twitter).not.toHaveProperty("images");
    expect(portfolioRobots()).toEqual({ rules: { userAgent: "*", disallow: "/" } });
    expect(portfolioSitemap()).toEqual([]);
  });

  it("canonicals every locale to its explicit route and lists the same five pages", () => {
    for (const locale of locales) {
      const metadata = portfolioMetadata(locale, copy, origin);
      expect(metadata.alternates?.canonical).toBe(`${origin}/${routeFromLocale(locale)}`);
      expect(metadata.alternates?.languages).toEqual({ en: `${origin}/en`, "pt-BR": `${origin}/br`, nl: `${origin}/nl`, es: `${origin}/es`, de: `${origin}/de`, "x-default": `${origin}/en` });
      expect(metadata.robots).toEqual({ index: true, follow: true });
      expect(metadata.openGraph).toMatchObject({ title: copy.title, description: copy.description, images: [{ url: `${origin}/portfolio/share.png`, width: 1200, height: 630, alt: copy.imageAlt }] });
      expect(metadata.twitter).toMatchObject({ card: "summary_large_image", images: [{ url: `${origin}/portfolio/share.png`, alt: copy.imageAlt }] });
    }
    expect(portfolioSitemap(origin).map((page) => page.url)).toEqual(locales.map((locale) => `${origin}/${routeFromLocale(locale)}`));
    expect(portfolioRobots(origin)).toEqual({ rules: { userAgent: "*", allow: "/" }, sitemap: `${origin}/sitemap.xml` });
  });
});
