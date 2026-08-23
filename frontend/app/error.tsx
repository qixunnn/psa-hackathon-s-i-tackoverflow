"use client";

import { useEffect } from "react";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-red-700">
        API error
      </p>
      <h1 className="mt-2 text-2xl font-semibold text-slate-950">
        Unable to load risk intelligence
      </h1>
      <p className="mt-3 max-w-xl leading-7 text-slate-600">
        Check that the backend is running and that the API base URL is configured,
        then try again.
      </p>
      <button
        type="button"
        onClick={reset}
        className="mt-6 rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
      >
        Try again
      </button>
    </section>
  );
}
