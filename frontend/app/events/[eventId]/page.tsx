import Link from "next/link";
import { notFound } from "next/navigation";

import { StatusBadge, SyntheticBadge } from "@/components/badges";
import { ApiError, getEventDetail } from "@/lib/api";
import { formatConfidence } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function EventDetailPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;

  let response;
  try {
    response = await getEventDetail(eventId);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const { event } = response;
  const routeExposure = event.routeExposure;

  return (
    <div className="space-y-8">
      <Link
        href="/"
        className="inline-flex text-sm font-semibold text-teal-700 transition hover:text-teal-900 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-600"
      >
        ← Global Risk Overview
      </Link>

      <article className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <header className="border-b border-slate-200 px-6 py-7 sm:px-8">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge value={event.severity} tone="severity" />
            <StatusBadge value={event.status} />
            {event.isSynthetic && <SyntheticBadge />}
          </div>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            {event.title}
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
            {event.summary}
          </p>
        </header>

        <dl className="grid gap-px bg-slate-200 sm:grid-cols-3">
          <DetailMetric label="Severity" value={event.severity} />
          <DetailMetric
            label="Confidence"
            value={formatConfidence(event.confidence)}
          />
          <DetailMetric label="Status" value={event.status} />
        </dl>

        <div className="grid gap-8 px-6 py-8 sm:px-8 lg:grid-cols-[0.8fr_1.2fr]">
          <section>
            <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
              Location
            </h2>
            <p className="mt-3 text-lg font-semibold text-slate-950">
              {event.primaryLocation.name}
            </p>
            {(event.primaryLocation.region || event.primaryLocation.country) && (
              <p className="mt-1 text-sm text-slate-600">
                {[event.primaryLocation.region, event.primaryLocation.country]
                  .filter(Boolean)
                  .join(", ")}
              </p>
            )}
          </section>

          <section>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                Route exposure
              </h2>
              {routeExposure && (
                <span className="text-xs font-semibold text-slate-500">
                  {routeExposure.resolved ? "Resolved" : "Under assessment"}
                </span>
              )}
            </div>

            {routeExposure ? (
              <div className="mt-3 space-y-6">
                <p className="leading-7 text-slate-700">
                  {routeExposure.explanation}
                </p>
                <RouteList
                  label="Affected trade corridors"
                  items={routeExposure.affectedTradeCorridors}
                />
                <RouteList
                  label="Alternative routes"
                  items={routeExposure.alternativeRoutes}
                />
              </div>
            ) : (
              <p className="mt-3 text-slate-600">Under assessment</p>
            )}
          </section>
        </div>
      </article>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 px-6 py-5 sm:px-8">
      <dt className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
        {label}
      </dt>
      <dd className="mt-1 text-base font-semibold text-slate-950">{value}</dd>
    </div>
  );
}

function RouteList({ label, items }: { label: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-950">{label}</h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">None identified</p>
      ) : (
        <ul className="mt-2 flex flex-wrap gap-2">
          {items.map((item) => (
            <li
              key={item}
              className="rounded-md border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-700"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
