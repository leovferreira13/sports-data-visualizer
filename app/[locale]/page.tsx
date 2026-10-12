import { notFound } from "next/navigation";

import { MethodologyContent } from "@/components/methodology-content";
import { PlayablePitch } from "@/components/playable-pitch";
import { localeFromRoute } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";

type PlaygroundPageProps = {
  params: Promise<{ locale: string }>;
};

export default async function PlaygroundPage({ params }: PlaygroundPageProps) {
  const { locale: routeLocale } = await params;
  const locale = localeFromRoute(routeLocale);

  if (!locale) {
    notFound();
  }

  const dictionary = await getDictionary(locale);

  return (
    <main>
      <section
        id="playground"
        className="playground"
        aria-labelledby="playground-title"
      >
        <section className="playground-copy" aria-labelledby="playground-title">
          <p className="eyebrow">{dictionary.playground.eyebrow}</p>
          <h1 id="playground-title">{dictionary.playground.title}</h1>
          <p className="lead">{dictionary.playground.description}</p>
        </section>

        <PlayablePitch locale={locale} copy={dictionary.playground} />
      </section>
      <MethodologyContent locale={locale} />
    </main>
  );
}
