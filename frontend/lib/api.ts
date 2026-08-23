import type {
  ApiErrorResponse,
  DemoArticleSummary,
  EventDetailResponse,
  EventListResponse,
  ProcessArticleResponse,
} from "@/types/api";

const DEFAULT_API_BASE_URL = "http://localhost:8000";
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL
).replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string,
    public readonly details: Record<string, unknown> | null = null,
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

export function getDemoArticles(): Promise<DemoArticleSummary[]> {
  return get<DemoArticleSummary[]>("/api/v1/demo/articles");
}

export function replayDemoArticle(
  articleId: string,
): Promise<ProcessArticleResponse> {
  return request<ProcessArticleResponse>(
    `/api/v1/demo/replay/${encodeURIComponent(articleId)}`,
    { method: "POST" },
  );
}

async function get<T>(path: string): Promise<T> {
  return request<T>(path, { method: "GET" });
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("The API could not be reached.", 0);
  }

  if (!response.ok) {
    const apiError = await parseApiError(response);
    throw new ApiError(
      apiError?.error.message ?? `The API returned status ${response.status}.`,
      response.status,
      apiError?.error.code,
      apiError?.error.details ?? null,
    );
  }

  return (await response.json()) as T;
}

async function parseApiError(response: Response): Promise<ApiErrorResponse | null> {
  try {
    const body = (await response.json()) as Partial<ApiErrorResponse>;
    if (
      typeof body.error?.code === "string" &&
      typeof body.error.message === "string"
    ) {
      return body as ApiErrorResponse;
    }
  } catch {
    // The HTTP status still provides a useful fallback for a non-JSON response.
  }

  return null;
}
