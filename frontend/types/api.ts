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
  developments: unknown[];
  latestScenarioRun?: unknown | null;
  latestOperationalImpact?: unknown | null;
  recommendations: unknown[];
}
