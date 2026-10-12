import { notFound, redirect } from "next/navigation";
import { localeFromRoute } from "@/lib/i18n/config";

// Preserve previously shared direct links after moving methodology below the pitch.
export default async function MethodologyRedirect({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!localeFromRoute(locale)) notFound();
  redirect(`/${locale}#methodology`);
}
