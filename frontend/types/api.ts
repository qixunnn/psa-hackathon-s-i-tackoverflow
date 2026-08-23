export type EventType =
  | "CHOKEPOINT_DISRUPTION"
  | "CANAL_CLOSURE"
  | "CARRIER_REROUTING"
  | "PORT_STRIKE"
  | "PORT_DISRUPTION"
  | "SEVERE_WEATHER"
  | "SECURITY_INCIDENT"
  | "TRADE_RESTRICTION"
  | "SANCTIONS"
  | "PIRACY"
  | "OTHER";

export type EventStatus =
  | "MONITORING"
  | "ACTIVE"
  | "ESCALATING"
  | "STABILISING"
  | "RESOLVED"
  | "ARCHIVED";

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Location {
  name: string;
  latitude?: number;
  longitude?: number;
  region?: string;
  country?: string;
}

export interface RouteExposure {
  chokepointIds: string[];
  affectedTradeCorridors: string[];
  alternativeRoutes: string[];
  explanation: string;
  resolved: boolean;
}

export interface Development {
  id: string;
  eventId: string;
  timestamp: string;
  title: string;
  summary: string;
  sourceIds: string[];
  evidenceIds: string[];
  previousSeverity?: Severity;
  newSeverity?: Severity;
  previousConfidence?: number;
  newConfidence?: number;
}

export interface Event {
  id: string;
  title: string;
  eventType: EventType;
  status: EventStatus;
  summary: string;
  primaryLocation: Location;
  severity: Severity;
  confidence: number;
  firstSeen: string;
  lastUpdated: string;
  sourceIds: string[];
  evidenceIds: string[];
  developmentIds: string[];
  routeExposure?: RouteExposure;
  latestScenarioRunId?: string;
  latestOperationalImpactId?: string;
  recommendationIds: string[];
  isSynthetic: boolean;
}

export interface EventSummary {
  id: string;
  title: string;
  eventType: EventType;
  status: EventStatus;
  severity: Severity;
  confidence: number;
  primaryLocation: Location;
  affectedTradeCorridors: string[];
  lastUpdated: string;
  isSynthetic: boolean;
}

export interface EventListResponse {
  items: EventSummary[];
  total: number;
}

export interface EventDetailResponse {
  event: Event;
  sources: unknown[];
  evidence: unknown[];
  developments: Development[];
  latestScenarioRun?: unknown | null;
  latestOperationalImpact?: unknown | null;
  recommendations: unknown[];
}

export interface DemoArticleSummary {
  id: string;
  title: string;
  publishedAt: string;
  processed: boolean;
}

export interface ProcessArticleResponse {
  articleId: string;
  maritimeRelevant: boolean;
  eventAction: "CREATED" | "UPDATED" | "NONE";
  eventId?: string | null;
  message: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown> | null;
  };
}
