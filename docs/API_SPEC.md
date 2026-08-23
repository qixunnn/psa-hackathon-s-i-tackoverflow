# API Specification

**Project:** PSA Global Watch  
**Version:** 1.0

---

# 1. Purpose

This document defines the HTTP API contract between the PSA Global Watch frontend and backend.

The API is intentionally small.

It exists to support the MVP workflow:

```text
Article
  ↓
Process / Replay
  ↓
Event created or updated
  ↓
Scenario analysis
  ↓
Operational impact
  ↓
Monitor / Prepare
  ↓
Dashboard + Activity Log
```

All frontend and backend implementation should conform to this contract unless the specification is explicitly updated.

---

# 2. API Principles

## 2.1 REST + JSON

The backend exposes REST endpoints using JSON request and response bodies.

---

## 2.2 Stable Contracts

Frontend code should not depend on undocumented response fields.

Backend code should not silently rename or remove shared fields.

Shared object definitions come from `DATA_SPEC.md`.

---

## 2.3 Consistent Error Format

All API errors should use the following shape:

```json
{
  "error": {
    "code": "EVENT_NOT_FOUND",
    "message": "The requested event could not be found.",
    "details": null
  }
}
```

---

## 2.4 UTC Timestamps

All timestamps returned by the API use ISO 8601 UTC format.

Example:

```text
2026-08-23T12:05:22Z
```

---

## 2.5 Confidence Format

Confidence values use:

```text
0.0 – 1.0
```

The frontend may display percentages.

---

# 3. Base Path

Recommended API base path:

```text
/api/v1
```

Example:

```text
GET /api/v1/events
```

---

# 4. Health Check

## GET `/health`

Used to verify that the backend is running.

### Response

**200 OK**

```json
{
  "status": "ok",
  "service": "psa-global-watch-api"
}
```

---

# 5. Process Article

## POST `/api/v1/articles/process`

Processes one normalized article through the Global Watch intelligence pipeline.

This endpoint is used for both:

- manually submitted articles
- replayed demo articles after normalization

### Request

```json
{
  "title": "Carrier suspends Red Sea transit",
  "content": "A shipping carrier has announced temporary rerouting...",
  "sourceName": "Demo Carrier Bulletin",
  "sourceType": "REPLAY_DATA",
  "url": null,
  "publishedAt": "2026-08-22T10:00:00Z",
  "isSynthetic": true
}
```

### Request Schema

```ts
interface ProcessArticleRequest {
  title: string;
  content: string;

  sourceName: string;
  sourceType: SourceType;

  url?: string | null;

  publishedAt: string;

  isSynthetic: boolean;
}
```

---

### Response

**200 OK**

```json
{
  "articleId": "ART-003",
  "maritimeRelevant": true,
  "eventAction": "UPDATED",
  "eventId": "EVT-001",
  "message": "Article processed successfully."
}
```

### Response Schema

```ts
interface ProcessArticleResponse {
  articleId: string;

  maritimeRelevant: boolean;

  eventAction:
    | "CREATED"
    | "UPDATED"
    | "NONE";

  eventId?: string | null;

  message: string;
}
```

---

### Irrelevant Article Example

```json
{
  "articleId": "ART-010",
  "maritimeRelevant": false,
  "eventAction": "NONE",
  "eventId": null,
  "message": "Article was not considered maritime relevant."
}
```

---

### Errors

**400 Bad Request**

Invalid input.

**422 Unprocessable Entity**

Input is valid JSON but violates schema rules.

**502 Bad Gateway**

AI service failed and processing could not complete.

**500 Internal Server Error**

Unexpected backend failure.

---

# 6. Replay Demo Article

## POST `/api/v1/demo/replay/{articleId}`

Processes one predefined synthetic demo article.

This endpoint exists primarily for deterministic hackathon demonstrations.

Example:

```text
POST /api/v1/demo/replay/red-sea-03
```

### Response

Same response schema as:

```text
POST /api/v1/articles/process
```

Example:

```json
{
  "articleId": "ART-003",
  "maritimeRelevant": true,
  "eventAction": "UPDATED",
  "eventId": "EVT-001",
  "message": "Demo article replayed successfully."
}
```

---

### Errors

**404 Not Found**

Requested demo article does not exist.

**409 Conflict**

Article has already been replayed and duplicate processing is disabled.

---

# 7. List Demo Articles

## GET `/api/v1/demo/articles`

Returns available replay articles.

This enables the frontend to provide demo controls without hardcoding filenames.

### Response

**200 OK**

```json
[
  {
    "id": "red-sea-01",
    "title": "Security incident reported near Bab el-Mandeb",
    "publishedAt": "2026-08-20T08:00:00Z",
    "processed": true
  },
  {
    "id": "red-sea-02",
    "title": "Independent maritime source confirms disruption",
    "publishedAt": "2026-08-21T09:00:00Z",
    "processed": false
  }
]
```

### Response Schema

```ts
interface DemoArticleSummary {
  id: string;
  title: string;
  publishedAt: string;
  processed: boolean;
}
```

---

# 8. List Events

## GET `/api/v1/events`

Returns Event summaries for the Global Risk Overview.

### Optional Query Parameters

```text
status
severity
limit
offset
```

Example:

```text
GET /api/v1/events?status=ACTIVE&severity=HIGH
```

---

### Response

**200 OK**

```json
{
  "items": [
    {
      "id": "EVT-001",
      "title": "Bab el-Mandeb Security Disruption",
      "eventType": "CHOKEPOINT_DISRUPTION",
      "status": "ESCALATING",
      "severity": "HIGH",
      "confidence": 0.84,
      "primaryLocation": {
        "name": "Bab el-Mandeb",
        "latitude": 12.58,
        "longitude": 43.33,
        "region": "Red Sea"
      },
      "affectedTradeCorridors": [
        "Asia-Europe"
      ],
      "lastUpdated": "2026-08-23T12:00:00Z",
      "isSynthetic": true
    }
  ],
  "total": 1
}
```

---

### EventSummary

```ts
interface EventSummary {
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
```

---

### Response Schema

```ts
interface EventListResponse {
  items: EventSummary[];
  total: number;
}
```

---

# 9. Get Event Detail

## GET `/api/v1/events/{eventId}`

Returns the complete event view used by the Event Detail page.

### Response

**200 OK**

```json
{
  "event": {
    "id": "EVT-001",
    "title": "Bab el-Mandeb Security Disruption",
    "eventType": "CHOKEPOINT_DISRUPTION",
    "status": "ESCALATING",
    "summary": "Security incidents near Bab el-Mandeb have led to increasing carrier rerouting activity.",
    "primaryLocation": {
      "name": "Bab el-Mandeb",
      "latitude": 12.58,
      "longitude": 43.33,
      "region": "Red Sea"
    },
    "severity": "HIGH",
    "confidence": 0.84,
    "firstSeen": "2026-08-20T08:00:00Z",
    "lastUpdated": "2026-08-23T12:00:00Z",
    "sourceIds": [
      "SRC-001",
      "SRC-002"
    ],
    "evidenceIds": [
      "EVD-001"
    ],
    "developmentIds": [
      "DEV-001",
      "DEV-002"
    ],
    "routeExposure": {
      "chokepointIds": [
        "CHK-BAB"
      ],
      "affectedTradeCorridors": [
        "Asia-Europe"
      ],
      "alternativeRoutes": [
        "Cape of Good Hope"
      ],
      "explanation": "The disruption may affect services using the Red Sea and Suez corridor.",
      "resolved": true
    },
    "latestScenarioRunId": "SCN-004",
    "latestOperationalImpactId": "IMP-004",
    "recommendationIds": [
      "REC-021",
      "REC-022"
    ],
    "isSynthetic": true
  },

  "sources": [],
  "evidence": [],
  "developments": [],
  "latestScenarioRun": null,
  "latestOperationalImpact": null,
  "recommendations": []
}
```

---

### Response Schema

```ts
interface EventDetailResponse {
  event: Event;

  sources: Source[];
  evidence: Evidence[];
  developments: Development[];

  latestScenarioRun?: ScenarioRun | null;

  latestOperationalImpact?: OperationalImpact | null;

  recommendations: Recommendation[];
}
```

The frontend should not need to make separate requests merely to render the initial Event Detail page.

---

### Errors

**404 Not Found**

```json
{
  "error": {
    "code": "EVENT_NOT_FOUND",
    "message": "The requested event could not be found.",
    "details": null
  }
}
```

---

# 10. Get Event Developments

## GET `/api/v1/events/{eventId}/developments`

Returns the Event Evolution timeline.

This endpoint is useful when timeline data needs independent refresh.

### Response

**200 OK**

```json
{
  "items": [
    {
      "id": "DEV-001",
      "eventId": "EVT-001",
      "timestamp": "2026-08-20T08:05:00Z",
      "title": "Initial disruption detected",
      "summary": "A security incident was reported near Bab el-Mandeb.",
      "sourceIds": [
        "SRC-001"
      ],
      "evidenceIds": [
        "EVD-001"
      ],
      "newSeverity": "MEDIUM",
      "newConfidence": 0.41
    }
  ]
}
```

### Response Schema

```ts
interface DevelopmentListResponse {
  items: Development[];
}
```

---

# 11. Get Event Sources and Evidence

## GET `/api/v1/events/{eventId}/evidence`

Returns evidence and associated sources for an Event.

### Response

```json
{
  "sources": [],
  "evidence": []
}
```

### Response Schema

```ts
interface EventEvidenceResponse {
  sources: Source[];
  evidence: Evidence[];
}
```

---

# 12. Get Scenario Configuration

## GET `/api/v1/events/{eventId}/scenario`

Returns the recommended scenario configuration for the selected Event.

This does not execute a new scenario.

### Response

**200 OK**

```json
{
  "eventId": "EVT-001",
  "scenarioType": "CARRIER_REROUTING",
  "assumptions": [
    {
      "id": "ASM-001",
      "name": "Carrier rerouting share",
      "minValue": 0.4,
      "maxValue": 0.7,
      "unit": "fraction",
      "reason": "Synthetic assumption used for the hackathon demonstration.",
      "sourceType": "SYNTHETIC_DEMO_DATA",
      "editable": true
    }
  ],
  "simulationRuns": 10000
}
```

The response conforms to `ScenarioInput`.

---

### Errors

**404 Not Found**

Event does not exist.

**422 Unprocessable Entity**

No scenario template can currently be mapped to the Event.

---

# 13. Run Scenario

## POST `/api/v1/events/{eventId}/scenario`

Executes a predefined deterministic scenario model.

The LLM must not create the mathematical model for this request.

### Request

```json
{
  "scenarioType": "CARRIER_REROUTING",
  "assumptions": [
    {
      "id": "ASM-001",
      "name": "Carrier rerouting share",
      "minValue": 0.4,
      "maxValue": 0.7,
      "unit": "fraction",
      "reason": "Synthetic demonstration assumption.",
      "sourceType": "USER_INPUT",
      "editable": true
    }
  ],
  "simulationRuns": 10000
}
```

### Request Schema

```ts
interface RunScenarioRequest {
  scenarioType: ScenarioType;
  assumptions: ScenarioAssumption[];
  simulationRuns?: number;
}
```

---

### Response

**200 OK**

```json
{
  "scenarioRun": {
    "id": "SCN-004",
    "eventId": "EVT-001",
    "scenarioType": "CARRIER_REROUTING",
    "createdAt": "2026-08-23T12:03:00Z",
    "assumptions": [],
    "simulationRuns": 10000,
    "metrics": [
      {
        "key": "additional_sailing_time",
        "label": "Additional sailing time",
        "value": 10.8,
        "lowerBound": 8.6,
        "upperBound": 13.1,
        "unit": "days"
      }
    ],
    "summary": "The scenario indicates increased schedule variability under the configured assumptions.",
    "disclaimer": "Results are conditional scenario outputs and should not be interpreted as validated predictions.",
    "isSynthetic": true
  },

  "operationalImpact": {
    "id": "IMP-004",
    "eventId": "EVT-001",
    "scenarioRunId": "SCN-004",
    "createdAt": "2026-08-23T12:03:02Z",
    "headline": "Potential increase in vessel arrival variability",
    "summary": "Affected services may experience additional schedule variability.",
    "implications": [],
    "confidence": 0.76,
    "isSynthetic": true
  },

  "recommendations": []
}
```

---

### Response Schema

```ts
interface RunScenarioResponse {
  scenarioRun: ScenarioRun;

  operationalImpact: OperationalImpact;

  recommendations: Recommendation[];
}
```

---

### Errors

**400 Bad Request**

Invalid assumption configuration.

**404 Not Found**

Event does not exist.

**422 Unprocessable Entity**

Scenario type is unsupported or required assumptions are missing.

**500 Internal Server Error**

Scenario execution failed.

---

# 14. List Scenario Runs

## GET `/api/v1/events/{eventId}/scenarios`

Returns previous Scenario Runs for an Event.

### Response

```json
{
  "items": []
}
```

### Response Schema

```ts
interface ScenarioRunListResponse {
  items: ScenarioRun[];
}
```

---

# 15. List Activity Logs

## GET `/api/v1/activity`

Returns system Activity Log entries.

### Optional Query Parameters

```text
eventId
articleId
stage
status
limit
offset
```

Example:

```text
GET /api/v1/activity?eventId=EVT-001
```

---

### Response

**200 OK**

```json
{
  "items": [
    {
      "id": "LOG-043",
      "timestamp": "2026-08-23T12:03:04Z",
      "eventId": "EVT-001",
      "articleId": "ART-004",
      "stage": "VERIFY",
      "action": "Independent source added",
      "result": "Confidence updated from 0.71 to 0.84",
      "status": "SUCCESS"
    }
  ],
  "total": 1
}
```

---

### Response Schema

```ts
interface ActivityListResponse {
  items: ActivityLog[];
  total: number;
}
```

The Activity API must never expose hidden chain-of-thought.

---

# 16. Optional MVP Dashboard Summary

## GET `/api/v1/dashboard/summary`

This endpoint is optional.

It may be useful to avoid multiple dashboard requests.

### Response

```json
{
  "activeEvents": 4,
  "criticalEvents": 1,
  "highEvents": 2,
  "recentUpdates": 3,
  "latestActivity": []
}
```

### Response Schema

```ts
interface DashboardSummaryResponse {
  activeEvents: number;
  criticalEvents: number;
  highEvents: number;
  recentUpdates: number;

  latestActivity: ActivityLog[];
}
```

Do not implement this endpoint if the frontend can efficiently derive the same information from existing APIs.

---

# 17. Pagination

For MVP simplicity, list endpoints may use:

```text
limit
offset
```

Example:

```text
GET /api/v1/events?limit=20&offset=0
```

Response:

```json
{
  "items": [],
  "total": 42
}
```

Cursor pagination is unnecessary for the hackathon MVP.

---

# 18. Sorting

Recommended default sorting:

## Events

```text
severity descending
lastUpdated descending
```

## Developments

```text
timestamp ascending
```

## Activity

```text
timestamp descending
```

## Scenario Runs

```text
createdAt descending
```

---

# 19. API Error Codes

Recommended application-level error codes:

```text
INVALID_REQUEST
ARTICLE_DUPLICATE
ARTICLE_NOT_FOUND
EVENT_NOT_FOUND
SCENARIO_NOT_SUPPORTED
SCENARIO_INPUT_INVALID
AI_SERVICE_UNAVAILABLE
AI_OUTPUT_INVALID
DATABASE_ERROR
INTERNAL_ERROR
```

Example:

```json
{
  "error": {
    "code": "SCENARIO_NOT_SUPPORTED",
    "message": "No predefined scenario model is available for this event.",
    "details": {
      "eventId": "EVT-001"
    }
  }
}
```

---

# 20. LLM Failure Behaviour

If the LLM fails during article processing:

1. Existing Event state must remain unchanged.
2. The failure must be recorded in Activity Log.
3. The request should return a controlled error.
4. The backend may retry once for malformed structured output.
5. The backend must not fabricate missing AI output.

Recommended response:

**502 Bad Gateway**

```json
{
  "error": {
    "code": "AI_SERVICE_UNAVAILABLE",
    "message": "The intelligence service is temporarily unavailable.",
    "details": null
  }
}
```

---

# 21. Duplicate Article Behaviour

Article deduplication should occur before expensive AI processing where possible.

If an identical article has already been processed, the backend may return:

**409 Conflict**

```json
{
  "error": {
    "code": "ARTICLE_DUPLICATE",
    "message": "This article has already been processed.",
    "details": {
      "existingArticleId": "ART-003"
    }
  }
}
```

For the demo replay system, duplicate handling may be configurable if repeated demonstrations are required.

---

# 22. Synthetic Data Behaviour

Any API object containing fabricated demonstration content must expose that fact.

Examples:

```json
{
  "isSynthetic": true
}
```

or:

```json
{
  "sourceType": "SYNTHETIC_DEMO_DATA"
}
```

The frontend should visibly label synthetic data.

---

# 23. Frontend Integration Rule

The frontend should primarily consume:

```text
GET  /events
GET  /events/{id}
POST /demo/replay/{id}
POST /events/{id}/scenario
GET  /activity
```

This is enough to build the complete MVP user experience.

Avoid adding endpoints simply because an individual component finds it convenient.

---

# 24. First Vertical Slice

The first end-to-end implementation milestone should require only:

```text
POST /api/v1/articles/process
GET  /api/v1/events
GET  /api/v1/events/{eventId}
```

Success criteria:

```text
Sample article
      ↓
POST /articles/process
      ↓
Event created
      ↓
GET /events
      ↓
Event appears
      ↓
GET /events/{id}
      ↓
Event detail appears
```

Scenario and Activity APIs should be added after this vertical slice works.

---

# 25. API Contract Change Rule

Once implementation begins:

```text
Proposed API change
       │
       ▼
Update API_SPEC.md
       │
       ▼
Check DATA_SPEC.md
       │
       ▼
Team agreement
       │
       ▼
Backend implementation
       │
       ▼
Frontend implementation
```

Do not silently modify shared response fields.

---

# 26. Definition of API Success

The API contract is successful when:

- the frontend can build using mock responses before the backend is complete
- backend developers know exactly what each endpoint must return
- Global Watch can persist results without frontend-specific assumptions
- Scenario developers can plug deterministic models into a stable endpoint
- all four developers can work independently without inventing new contracts

For the MVP, the most important endpoints are:

```text
POST /api/v1/articles/process
POST /api/v1/demo/replay/{articleId}

GET  /api/v1/events
GET  /api/v1/events/{eventId}

GET  /api/v1/events/{eventId}/scenario
POST /api/v1/events/{eventId}/scenario

GET  /api/v1/activity
```