# Portfolio presentation and deployment metadata

**Status:** pre-release presentation implemented in #25; actual-domain verification and live links complete with #26.

## Responsibilities

`lib/project.ts` holds Leonardo Ferreira's identity and confirmed GitHub, LinkedIn and repository URLs. `app/[locale]/page.tsx` renders a compact author line after the existing introduction; labels come from all five locale dictionaries. No extra client state or tracking is introduced. The existing scene, model and attribution footer are retained.

`lib/portfolio-metadata.ts` supplies localized title/description/preview alt text, author metadata, Open Graph/Twitter cards, canonical and language-alternate links. The layout remains the locale metadata boundary. `app/icon.svg` is an original project icon; it is not a third-party brand asset. `app/robots.ts` and `app/sitemap.ts` expose the Next.js metadata routes.

## Origin contract

Set `SITE_URL` to the final public HTTPS origin at **build time**, for example the confirmed Railway-generated origin. It must contain no credentials, nonstandard port, path beyond `/`, query or fragment. Invalid or blank supplied values fail validation. Localhost, local names and IP literals are rejected. The origin is public configuration, not a secret, and is never inferred from a request header.

With a configured origin:

- Each `/en`, `/br`, `/nl`, `/es` and `/de` page canonicals to itself.
- Alternate links use `en`, `pt-BR`, `nl`, `es`, `de`; `x-default` points to `/en`. The preference-dependent root route is not a canonical page.
- OG and Twitter share-image URLs are absolute and reference `/portfolio/share.png` (1200 × 630); title/description/alt text remain localized. One English screenshot-based preview is shared across languages.
- Robots allows crawling and advertises the sitemap; the sitemap lists only the five explicit pages and their alternates. It includes no methodology fragments, obsolete redirect routes or model files.

Without SITE_URL, the app still builds and runs: robots disallows crawling, page metadata uses noindex/nofollow, and the sitemap is empty. Canonical, alternate and share-image URL tags are omitted. This is a small deviation from the proposed relative local OG image: Next.js requires/resolves absolute social image URLs, so omission avoids localhost-derived metadata. The static preview remains directly available locally.

Metadata routes and pages are prerendered. **Rebuild/redeploy after changing SITE_URL**; changing only the running server's environment does not update already built metadata. Recovery is correction plus rebuild, or restoring the previous reviewed deployment through #26.

## Assets and review

`assets/portfolio/playground.png` captures the actual English app with an illustrative preset for README. `public/portfolio/share.png` composes that app capture with a readable project/author heading. Neither contains source rows or a historical match reconstruction. The source/logo footer remains intact; a screenshot of the Playground is not a replacement for attribution.

See [portfolio QA](../../reports/portfolio-presentation-qa.md) for capture context, actual checks and editorial exceptions. Generated scientific reports, machine evidence, original parameters, protocols and checksums are not edited for portfolio tone. Current explanatory prose distinguishes reported local reproduction from independently inspected aggregates.

## Railway completion (#26)

1. Set the confirmed HTTPS origin as SITE_URL before the production build.
2. Add the actual live `/en` URL to README after observing deployment success.
3. Inspect heads, images/icon, robots and sitemap on all five live routes; verify unauthenticated repository/app access and a share preview where available.
4. Refresh asset/network/source/logo checks for the exact release commit/build, including the outstanding per-asset branding guidance.
5. Record observed outcomes and limitations. Local checks do not establish live crawler/social-platform behavior or physical-device QA.
