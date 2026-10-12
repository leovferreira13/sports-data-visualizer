"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Dictionary } from "@/lib/i18n/dictionaries";

export function SectionNavigation({
  route,
  copy,
}: {
  route: string;
  copy: Dictionary["navigation"];
}) {
  const pathname = usePathname();
  return (
    <nav className="section-navigation" aria-label={copy.label}>
      <Link
        href={`/${route}`}
        aria-current={pathname === `/${route}` ? "page" : undefined}
      >
        {copy.playground}
      </Link>
      <Link
        href={`/${route}/methodology`}
        aria-current={pathname === `/${route}/methodology` ? "page" : undefined}
      >
        {copy.methodology}
      </Link>
    </nav>
  );
}
