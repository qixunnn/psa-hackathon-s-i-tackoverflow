"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { StatusBadge, SyntheticBadge } from "@/components/badges";
import {
  ApiError,
  getDemoArticles,
  getEventDetail,
  replayDemoArticle,
} from "@/lib/api";
import { formatConfidence, formatUtcTimestamp } from "@/lib/format";
import type {
  DemoArticleSummary,
  Development,
  EventDetailResponse,
} from "@/types/api";

interface EventDetailExperienceProps {
  initialDetail: EventDetailResponse;
  initialDemoArticles: DemoArticleSummary[];
}

interface Feedback {
  tone: "success" | "error";
  message: string;
}

export function EventDetailExperience({
  initialDetail,
  initialDemoArticles,
}: EventDetailExperienceProps) {
  const [detail, setDetail] = useState(initialDetail);
  const [demoArticles, setDemoArticles] = useState(initialDemoArticles);
  const [pendingReplayId, setPendingReplayId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const { event } = detail;
  const routeExposure = event.routeExposure;

  async function refreshData() {
    const [nextDetail, nextDemoArticles] = await Promise.all([
      getEventDetail(event.id),
      getDemoArticles(),
    ]);
    setDetail(nextDetail);
    setDemoArticles(nextDemoArticles);
  }

  async function handleReplay(article: DemoArticleSummary) {
    setPendingReplayId(article.id);
    setFeedback(null);

    try {
      const result = await replayDemoArticle(article.id);
      await refreshData();
      setFeedback({ tone: "success", message: result.message });
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        try {
          await refreshData();
        } catch {
          setFeedback({
            tone: "error",
            message:
              "This article was already processed, but the latest data could not be loaded.",
          });
          return;
        }

        setFeedback({
          tone: "error",
          message: "This article has already been processed. The latest data is shown.",
        });
      } else if (error instanceof ApiError && error.status === 0) {
        setFeedback({
          tone: "error",
          message: "The backend is unavailable. Check that the API is running and try again.",
        });
      } else {
        setFeedback({
          tone: "error",
          message:
            error instanceof Error
              ? error.message
              : "The demo article could not be replayed.",
        });
      }
    } finally {
      setPendingReplayId(null);
    }
  }

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

      <div className="grid items-start gap-6 lg:grid-cols-[1.35fr_0.85fr]">
        <EventEvolution developments={detail.developments} />
        <DemoReplayPanel
          articles={demoArticles}
          feedback={feedback}
          pendingReplayId={pendingReplayId}
          onReplay={handleReplay}
        />
      </div>
    </div>
  );
}

function EventEvolution({ developments }: { developments: Development[] }) {
  const chronologicalDevelopments = useMemo(
    () =>
      [...developments].sort(
        (left, right) =>
          new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime(),
      ),
    [developments],
  );

  return (
    <section
      aria-labelledby="event-evolution-heading"
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
    >
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-teal-700">
        Timeline
      </p>
      <h2
        id="event-evolution-heading"
        className="mt-2 text-2xl font-semibold tracking-tight text-slate-950"
      >
        Event Evolution
      </h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        Chronological changes to this event assessment.
      </p>

      {chronologicalDevelopments.length === 0 ? (
        <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center">
          <p className="font-semibold text-slate-800">No developments yet</p>
          <p className="mt-1 text-sm text-slate-500">
            Replay an unprocessed demo article to add the first update.
          </p>
        </div>
      ) : (
        <ol className="mt-7 space-y-0">
          {chronologicalDevelopments.map((development, index) => (
            <li
              key={development.id}
              className="relative grid grid-cols-[1.25rem_1fr] gap-4 pb-8 last:pb-0"
            >
              {index < chronologicalDevelopments.length - 1 && (
                <span
                  aria-hidden="true"
                  className="absolute left-[0.5625rem] top-5 h-full w-px bg-slate-200"
                />
              )}
              <span
                aria-hidden="true"
                className="relative mt-1.5 size-5 rounded-full border-4 border-teal-100 bg-teal-600"
              />
              <article>
                <time
                  dateTime={development.timestamp}
                  className="text-xs font-semibold uppercase tracking-[0.1em] text-slate-500"
                >
                  {formatUtcTimestamp(development.timestamp)}
                </time>
                <h3 className="mt-2 text-lg font-semibold text-slate-950">
                  {development.title}
                </h3>
                <p className="mt-2 leading-7 text-slate-600">
                  {development.summary}
                </p>
                <DevelopmentChanges development={development} />
              </article>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

function DevelopmentChanges({ development }: { development: Development }) {
  const previousSeverity = development.previousSeverity;
  const newSeverity = development.newSeverity;
  const previousConfidence = development.previousConfidence;
  const newConfidence = development.newConfidence;
  const severityChanged =
    typeof previousSeverity === "string" &&
    typeof newSeverity === "string" &&
    previousSeverity !== newSeverity;
  const confidenceChanged =
    typeof previousConfidence === "number" &&
    typeof newConfidence === "number" &&
    previousConfidence !== newConfidence;

  if (!severityChanged && !confidenceChanged) {
    return null;
  }

  return (
    <dl className="mt-4 flex flex-wrap gap-3">
      {severityChanged && (
        <div className="rounded-lg border border-orange-200 bg-orange-50 px-3 py-2">
          <dt className="text-xs font-semibold uppercase tracking-wide text-orange-700">
            Severity
          </dt>
          <dd className="mt-1 flex items-center gap-2 text-sm font-bold text-slate-900">
            <span>{previousSeverity}</span>
            <span aria-hidden="true" className="text-orange-600">
              →
            </span>
            <span>{newSeverity}</span>
          </dd>
        </div>
      )}
      {confidenceChanged && (
        <div className="rounded-lg border border-teal-200 bg-teal-50 px-3 py-2">
          <dt className="text-xs font-semibold uppercase tracking-wide text-teal-700">
            Confidence
          </dt>
          <dd className="mt-1 text-sm font-bold text-slate-900">
            {formatConfidence(previousConfidence)}
            <span aria-hidden="true" className="mx-2 text-teal-600">
              →
            </span>
            {formatConfidence(newConfidence)}
          </dd>
        </div>
      )}
    </dl>
  );
}

function DemoReplayPanel({
  articles,
  feedback,
  pendingReplayId,
  onReplay,
}: {
  articles: DemoArticleSummary[];
  feedback: Feedback | null;
  pendingReplayId: string | null;
  onReplay: (article: DemoArticleSummary) => Promise<void>;
}) {
  return (
    <section
      aria-labelledby="demo-replay-heading"
      className="rounded-xl border border-amber-200 bg-amber-50/40 p-6 shadow-sm"
    >
      <SyntheticBadge />
      <h2
        id="demo-replay-heading"
        className="mt-4 text-xl font-semibold text-slate-950"
      >
        Demo article replay
      </h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">
        Replay predefined synthetic articles to advance the event deterministically.
      </p>

      {feedback && (
        <div
          aria-live="polite"
          className={`mt-4 rounded-md border px-3 py-2.5 text-sm font-medium ${
            feedback.tone === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-red-200 bg-red-50 text-red-800"
          }`}
        >
          {feedback.message}
        </div>
      )}

      {articles.length === 0 ? (
        <p className="mt-5 rounded-lg border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600">
          No demo articles are available.
        </p>
      ) : (
        <ol className="mt-5 space-y-3">
          {articles.map((article) => {
            const isPending = pendingReplayId === article.id;
            return (
              <li
                key={article.id}
                className="rounded-lg border border-slate-200 bg-white p-4"
              >
                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide">
                  <span className="text-amber-700">Synthetic</span>
                  <span className="text-slate-300" aria-hidden="true">
                    /
                  </span>
                  <span
                    className={
                      article.processed ? "text-emerald-700" : "text-slate-500"
                    }
                  >
                    {article.processed ? "Processed" : "Ready to replay"}
                  </span>
                </div>
                <h3 className="mt-2 text-sm font-semibold leading-6 text-slate-900">
                  {article.title}
                </h3>
                <time
                  dateTime={article.publishedAt}
                  className="mt-1 block text-xs text-slate-500"
                >
                  {formatUtcTimestamp(article.publishedAt)}
                </time>
                <button
                  type="button"
                  disabled={article.processed || pendingReplayId !== null}
                  onClick={() => void onReplay(article)}
                  className="mt-3 inline-flex w-full items-center justify-center rounded-md bg-slate-950 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-600 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
                >
                  {article.processed
                    ? "Already processed"
                    : isPending
                      ? "Replaying…"
                      : "Replay article"}
                </button>
              </li>
            );
          })}
        </ol>
      )}
    </section>
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
