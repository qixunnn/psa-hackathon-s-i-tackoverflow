import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "PSA Global Watch",
    template: "%s | PSA Global Watch",
  },
  description: "Global Maritime Risk Intelligence for PSA.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-50">
          <header className="border-b border-slate-800 bg-slate-950 text-white">
            <div className="mx-auto flex max-w-6xl flex-col gap-5 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-8">
              <Link href="/" className="inline-flex items-center gap-3">
                <span
                  aria-hidden="true"
                  className="grid size-10 place-items-center rounded-lg bg-teal-500 text-sm font-bold text-slate-950"
                >
                  GW
                </span>
                <span>
                  <span className="block text-base font-semibold tracking-wide">
                    PSA Global Watch
                  </span>
                  <span className="block text-xs text-slate-400">
                    Maritime Risk Intelligence
                  </span>
                </span>
              </Link>

              <nav aria-label="Primary navigation">
                <Link
                  href="/"
                  className="inline-flex rounded-md bg-slate-800 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-400"
                >
                  Global Risk Overview
                </Link>
              </nav>
            </div>
          </header>

          <main className="mx-auto w-full max-w-6xl px-5 py-10 sm:px-8 sm:py-14">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
