import { notFound } from "next/navigation";

import { xgEvidence } from "@/lib/xg-evidence";
import { PlayablePitch } from "@/components/playable-pitch";
import { localeFromRoute } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";

type PlaygroundPageProps = {
  params: Promise<{ locale: string }>;
};

export default async function PlaygroundPage({
  params,
}: PlaygroundPageProps) {
  const { locale: routeLocale } = await params;
  const locale = localeFromRoute(routeLocale);

  if (!locale) {
    notFound();
  }

  const dictionary = await getDictionary(locale);

  return (
    <main className="playground">
      <section className="playground-copy" aria-labelledby="playground-title">
        <p className="eyebrow">{dictionary.playground.eyebrow}</p>
        <h1 id="playground-title">{dictionary.playground.title}</h1>
        <p className="lead">{dictionary.playground.description}</p>
        <p className="status">{dictionary.playground.status}</p>
      </section>

      <PlayablePitch locale={locale} copy={dictionary.playground} presetSupport={Object.fromEntries(xgEvidence.scene_audit.diagnostics.map(item => [item.scene, item.support_category]))} />
    </main>
  );
}
