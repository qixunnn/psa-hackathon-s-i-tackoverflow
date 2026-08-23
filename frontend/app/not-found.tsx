import Link from "next/link";

export default function NotFound() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
      <p className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
        404
      </p>
      <h1 className="mt-2 text-2xl font-semibold text-slate-950">
        Event not found
      </h1>
      <p className="mt-3 text-slate-600">
        The requested maritime event does not exist or is no longer available.
      </p>
      <Link
        href="/"
        className="mt-6 inline-flex rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600"
      >
        Return to overview
      </Link>
    </section>
  );
}
