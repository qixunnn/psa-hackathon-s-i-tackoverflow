import { EventCard } from "@/components/event-card";
import { StatePanel } from "@/components/state-panel";
import { getEvents } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function GlobalRiskOverviewPage() {
  const events = await getEvents();

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">
            Maritime intelligence
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            Global Risk Overview
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
            Tracked disruptions with potential relevance to maritime routes and
            operational planning.
          </p>
        </div>
        <p className="text-sm text-slate-500">
          {events.total} {events.total === 1 ? "event" : "events"}
        </p>
      </header>

      {events.items.length === 0 ? (
        <StatePanel
          title="No events to display"
          description="There are currently no maritime disruptions in the event feed."
        />
      ) : (
        <section aria-label="Tracked maritime events" className="grid gap-5">
          {events.items.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
        </section>
      )}
    </div>
  );
}
