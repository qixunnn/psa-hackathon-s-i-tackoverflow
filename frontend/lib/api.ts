import type { EventDetailResponse, EventListResponse } from "@/types/api";

const DEFAULT_API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getEvents(): Promise<EventListResponse> {
  return get<EventListResponse>("/api/v1/events");
}

export function getEventDetail(eventId: string): Promise<EventDetailResponse> {
  return get<EventDetailResponse>(`/api/v1/events/${encodeURIComponent(eventId)}`);
}

async function get<T>(path: string): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("The API could not be reached.", 0);
  }

  if (!response.ok) {
    throw new ApiError(`The API returned status ${response.status}.`, response.status);
  }

  return (await response.json()) as T;
}
