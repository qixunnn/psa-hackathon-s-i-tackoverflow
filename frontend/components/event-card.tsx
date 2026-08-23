import Link from "next/link";

import { StatusBadge, SyntheticBadge } from "@/components/badges";
import { formatConfidence, formatUtcTimestamp } from "@/lib/format";
import type { EventSummary } from "@/types/api";

export function EventCard({ event }: { event: EventSummary }) {
  return (
    <Link
      href={`/events/${event.id}`}
      className="group block rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-600 sm:p-7"
    >
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge value={event.severity} tone="severity" />
            <StatusBadge value={event.status} />
            {event.isSynthetic && <SyntheticBadge />}
          </div>
          <h2 className="mt-4 text-xl font-semibold text-slate-950 transition group-hover:text-teal-800 sm:text-2xl">
            {event.title}
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            {event.primaryLocation.name}
            {event.primaryLocation.region
              ? ` · ${event.primaryLocation.region}`
              : ""}
          </p>
        </div>

        <dl className="grid shrink-0 grid-cols-2 gap-x-8 gap-y-4 text-sm sm:grid-cols-3 lg:min-w-xl">
          <DataPoint
            label="Confidence"
            value={formatConfidence(event.confidence)}
          />
          <DataPoint
            label="Trade corridor"
            value={event.affectedTradeCorridors.join(", ") || "Under assessment"}
          />
          <DataPoint
            label="Last updated"
            value={formatUtcTimestamp(event.lastUpdated)}
            wide
          />
        </dl>
      </div>
    </Link>
  );
}

function DataPoint({
  label,
  value,
  wide = false,
}: {
  label: string;
  value: string;
  wide?: boolean;
}) {
  return (
    <div className={wide ? "col-span-2 sm:col-span-1" : undefined}>
      <dt className="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500">
        {label}
      </dt>
      <dd className="mt-1 font-medium text-slate-900">{value}</dd>
    </div>
  );
}
