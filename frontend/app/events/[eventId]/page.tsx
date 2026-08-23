import { notFound } from "next/navigation";

import { EventDetailExperience } from "@/components/event-detail-experience";
import { ApiError, getDemoArticles, getEventDetail } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function EventDetailPage({
  params,
}: {
  params: Promise<{ eventId: string }>;
}) {
  const { eventId } = await params;

  let response;
  let demoArticles;
  try {
    [response, demoArticles] = await Promise.all([
      getEventDetail(eventId),
      getDemoArticles(),
    ]);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return <EventDetailExperience initialDetail={response} initialDemoArticles={demoArticles} />;
}
