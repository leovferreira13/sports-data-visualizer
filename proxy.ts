import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { localeCookieName } from "@/lib/i18n/config";
import { resolveLocale } from "@/lib/i18n/resolve-locale";

export function proxy(request: NextRequest) {
  const savedLocale = request.cookies.get(localeCookieName)?.value;
  const locale = resolveLocale(
    savedLocale,
    request.headers.get("accept-language"),
  );

  const target = request.nextUrl.clone();
  target.pathname = `/${locale}`;

  return NextResponse.redirect(target);
}

export const config = {
  matcher: ["/"],
};
