import { notFound } from "next/navigation";

import { localeFromRoute } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";

type PlaygroundPageProps = {
  params: Promise<{ lang: string }>;
};

export default async function PlaygroundPage({
  params,
}: PlaygroundPageProps) {
  const { lang } = await params;
  const locale = localeFromRoute(lang);

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

      <section className="pitch-placeholder" aria-hidden="true">
        <div className="halfway-line" />
        <div className="penalty-area" />
        <div className="goal-area" />
        <div className="penalty-arc" />
      </section>
    </main>
  );
}
