import type { ReactNode } from "react";

import "../[locale]/globals.css";

export default function DevLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="site-shell">{children}</div>
      </body>
    </html>
  );
}
