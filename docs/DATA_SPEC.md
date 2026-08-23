# Data Specification

**Project:** PSA Global Watch  
**Version:** 1.0

---

# 1. Purpose

This document defines the shared domain models used across PSA Global Watch.

These models are the contract between:

1. Global Watch / AI
2. Backend / Data
3. Scenario / Risk
4. Frontend

The purpose is to prevent different parts of the system from inventing incompatible representations of the same data.

All implementations should conform to this document.

---

# 2. Data Design Principles

## 2.1 Event Is the Core Domain Object

The central object in the system is an `Event`.

An Event represents a persistent real-world maritime disruption.

Articles are not Events.

Multiple articles may provide evidence and developments for the same Event.

Example:

```text
Article A ─┐
Article B ─┼──► EVT-001: Bab el-Mandeb Disruption
Article C ─┘
```

---

## 2.2 Evidence Must Be Traceable

Claims used by the system should be traceable to their source.

The system should distinguish between:

- source material
- extracted evidence
- scenario assumptions
- deterministic outputs
- AI-generated interpretation

---

## 2.3 Synthetic Data Must Be Labelled

Any invented data used for demonstration must be explicitly marked as:

```text
SYNTHETIC_DEMO_DATA
```

Synthetic data must never be presented as real PSA operational data.

---

## 2.4 Confidence and Severity Are Different

`confidence` represents how strongly the available evidence supports the current assessment.

`severity` represents the potential significance of the disruption.

A high-severity Event may still have low confidence.

Example:

```text
Potential Strait Closure

Severity: CRITICAL
Confidence: 0.42
```

---

# 3. Shared Enumerations

Enums should be shared across backend and frontend.

---

## 3.1 EventType

```text
CHOKEPOINT_DISRUPTION
CANAL_CLOSURE
CARRIER_REROUTING
PORT_STRIKE
PORT_DISRUPTION
SEVERE_WEATHER
SECURITY_INCIDENT
TRADE_RESTRICTION
SANCTIONS
PIRACY
OTHER
```

---

## 3.2 EventStatus

```text
MONITORING
ACTIVE
ESCALATING
STABILISING
RESOLVED
ARCHIVED
```

---

## 3.3 Severity

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## 3.4 SourceType

```text
NEWS
MARITIME_BULLETIN
CARRIER_ADVISORY
AUTHORITY_NOTICE
WEATHER_SOURCE
REPLAY_DATA
OTHER
```

---

## 3.5 AssumptionSourceType

```text
EXTERNAL_SOURCE
SYSTEM_CONFIG
AI_EXTRACTION
USER_INPUT
SYNTHETIC_DEMO_DATA
```

---

## 3.6 RecommendationType

```text
MONITOR
PREPARE
```

---

## 3.7 ActivityStage

```text
OBSERVE
INTERPRET
VERIFY
MODEL
ASSESS
RECOMMEND
SYSTEM
```

---

## 3.8 ActivityStatus

```text
SUCCESS
WARNING
FAILED
INFO
```

---

## 3.9 ScenarioType

```text
CARRIER_REROUTING
CHOKEPOINT_DISRUPTION
CANAL_CLOSURE
PORT_STRIKE
SEVERE_WEATHER
TRADE_RESTRICTION
```

---

# 4. Canonical Article

`Article` represents normalized source content entering the intelligence pipeline.

```ts
interface Article {
  id: string;

  title: string;
  content: string;

  sourceName: string;
  sourceType: SourceType;

  url?: string;

  publishedAt: string;
  ingestedAt: string;

  isSynthetic: boolean;

  contentHash?: string;
}
```

---

## Field Definitions

### `id`

Unique internal identifier.

Example:

```text
ART-001
```

---

### `title`

Original article or bulletin title.

---

### `content`

Normalized article body or relevant extracted text.

---

### `sourceName`

Human-readable source name.

Example:

```text
Reuters
```

or:

```text
Demo Maritime News
```

---

### `sourceType`

Classification of the source.

---

### `url`

Original source URL where available.

Replay/demo content may omit this.

---

### `publishedAt`

Publication timestamp.

ISO 8601 format.

Example:

```text
2026-08-20T08:00:00Z
```

---

### `ingestedAt`

Timestamp when Global Watch received the article.

---

### `isSynthetic`

Must be `true` for replayed or fabricated demo content.

---

### `contentHash`

Optional hash used for article deduplication.

---

# 5. Source

`Source` represents a source attached to an Event.

```ts
interface Source {
  id: string;

  articleId?: string;

  name: string;
  type: SourceType;

  url?: string;

  publishedAt?: string;

  isIndependent: boolean;
  isSynthetic: boolean;
}
```

Example:

```json
{
  "id": "SRC-003",
  "articleId": "ART-003",
  "name": "Demo Carrier Bulletin",
  "type": "CARRIER_ADVISORY",
  "publishedAt": "2026-08-22T10:00:00Z",
  "isIndependent": true,
  "isSynthetic": true
}
```

---

# 6. Evidence

`Evidence` represents a specific factual claim extracted from a Source.

```ts
interface Evidence {
  id: string;

  eventId: string;
  sourceId: string;

  claim: string;

  evidenceType?: string;

  extractedAt: string;

  sourceExcerpt?: string;
}
```

Example:

```json
{
  "id": "EVD-008",
  "eventId": "EVT-001",
  "sourceId": "SRC-003",
  "claim": "The carrier announced temporary rerouting away from the Red Sea.",
  "evidenceType": "CARRIER_REROUTING",
  "extractedAt": "2026-08-22T10:05:00Z"
}
```

`sourceExcerpt` should remain short.

It exists to support traceability, not to reproduce entire source articles.

---

# 7. Location

```ts
interface Location {
  name: string;

  latitude?: number;
  longitude?: number;

  region?: string;
  country?: string;
}
```

Example:

```json
{
  "name": "Bab el-Mandeb",
  "latitude": 12.58,
  "longitude": 43.33,
  "region": "Red Sea"
}
```

Coordinates should normally come from the Maritime Knowledge Layer rather than the LLM.

---

# 8. Chokepoint

```ts
interface Chokepoint {
  id: string;

  name: string;

  location: Location;

  connectedRegions: string[];

  majorTradeCorridors: string[];

  alternativeRoutes: string[];

  supportedScenarios: ScenarioType[];
}
```

Example:

```json
{
  "id": "CHK-BAB",
  "name": "Bab el-Mandeb",
  "location": {
    "name": "Bab el-Mandeb",
    "latitude": 12.58,
    "longitude": 43.33,
    "region": "Red Sea"
  },
  "connectedRegions": [
    "Red Sea",
    "Gulf of Aden"
  ],
  "majorTradeCorridors": [
    "Asia-Europe"
  ],
  "alternativeRoutes": [
    "Cape of Good Hope"
  ],
  "supportedScenarios": [
    "CHOKEPOINT_DISRUPTION",
    "CARRIER_REROUTING"
  ]
}
```

---

# 9. RouteExposure

`RouteExposure` explains how an Event may affect maritime movement.

```ts
interface RouteExposure {
  chokepointIds: string[];

  affectedTradeCorridors: string[];

  alternativeRoutes: string[];

  explanation: string;

  resolved: boolean;
}
```

Example:

```json
{
  "chokepointIds": [
    "CHK-BAB"
  ],
  "affectedTradeCorridors": [
    "Asia-Europe"
  ],
  "alternativeRoutes": [
    "Cape of Good Hope"
  ],
  "explanation": "Disruption near Bab el-Mandeb may affect services using the Red Sea and Suez route.",
  "resolved": true
}
```

---

# 10. Development

A `Development` represents a chronological update to an Event.

This is what powers Event Evolution.

```ts
interface Development {
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
```

Example:

```json
{
  "id": "DEV-003",
  "eventId": "EVT-001",
  "timestamp": "2026-08-22T10:05:00Z",
  "title": "Carrier announces rerouting",
  "summary": "A carrier advisory confirmed temporary rerouting away from the Red Sea.",
  "sourceIds": [
    "SRC-003"
  ],
  "evidenceIds": [
    "EVD-008"
  ],
  "previousSeverity": "MEDIUM",
  "newSeverity": "HIGH",
  "previousConfidence": 0.63,
  "newConfidence": 0.82
}
```

---

# 11. Event

`Event` is the canonical domain object.

```ts
interface Event {
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
```

---

## Example Event

```json
{
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
    "SRC-002",
    "SRC-003"
  ],
  "evidenceIds": [
    "EVD-001",
    "EVD-004",
    "EVD-008"
  ],
  "developmentIds": [
    "DEV-001",
    "DEV-002",
    "DEV-003"
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
    "explanation": "The disruption may affect vessels normally travelling through the Red Sea and Suez corridor.",
    "resolved": true
  },
  "latestScenarioRunId": "SCN-004",
  "latestOperationalImpactId": "IMP-004",
  "recommendationIds": [
    "REC-021",
    "REC-022"
  ],
  "isSynthetic": true
}
```

---

# 12. Confidence

Confidence must use a normalized range:

```text
0.00 – 1.00
```

Examples:

```text
0.22
0.67
0.91
```

The API must not alternate between:

```text
0.84
```

and:

```text
84
```

The frontend may display:

```text
84%
```

but the canonical stored/API value is:

```text
0.84
```

---

# 13. Confidence Inputs

The final confidence score should be produced by deterministic application logic.

Possible inputs include:

```ts
interface ConfidenceInputs {
  independentSourceCount: number;

  authorityConfirmation: boolean;
  carrierConfirmation: boolean;

  evidenceConsistencyScore: number;

  sourceQualityScore?: number;
}
```

The exact formula may evolve during implementation.

The LLM may provide supporting signals but must not assign the final confidence value directly.

---

# 14. ScenarioAssumption

```ts
interface ScenarioAssumption {
  id: string;

  name: string;

  value?: number;
  minValue?: number;
  maxValue?: number;

  unit?: string;

  reason: string;

  sourceType: AssumptionSourceType;

  sourceReference?: string;

  editable: boolean;
}
```

Example:

```json
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
```

---

# 15. ScenarioInput

```ts
interface ScenarioInput {
  eventId: string;

  scenarioType: ScenarioType;

  assumptions: ScenarioAssumption[];

  simulationRuns?: number;
}
```

Example:

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
      "reason": "Synthetic demonstration assumption.",
      "sourceType": "SYNTHETIC_DEMO_DATA",
      "editable": true
    }
  ],
  "simulationRuns": 10000
}
```

---

# 16. ScenarioMetric

`ScenarioMetric` stores deterministic or simulated numerical results.

```ts
interface ScenarioMetric {
  key: string;

  label: string;

  value?: number;

  lowerBound?: number;
  upperBound?: number;

  unit?: string;

  description?: string;
}
```

Example:

```json
{
  "key": "additional_sailing_time",
  "label": "Additional sailing time",
  "value": 10.8,
  "lowerBound": 8.6,
  "upperBound": 13.1,
  "unit": "days",
  "description": "Median result under the current scenario assumptions."
}
```

---

# 17. ScenarioRun

```ts
interface ScenarioRun {
  id: string;

  eventId: string;

  scenarioType: ScenarioType;

  createdAt: string;

  assumptions: ScenarioAssumption[];

  simulationRuns?: number;

  metrics: ScenarioMetric[];

  summary: string;

  disclaimer: string;

  isSynthetic: boolean;
}
```

Example:

```json
{
  "id": "SCN-004",
  "eventId": "EVT-001",
  "scenarioType": "CARRIER_REROUTING",
  "createdAt": "2026-08-23T12:03:00Z",
  "simulationRuns": 10000,
  "assumptions": [],
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
  "summary": "The scenario indicates increased schedule variability under the configured rerouting assumptions.",
  "disclaimer": "Results are conditional scenario outputs and should not be interpreted as validated predictions.",
  "isSynthetic": true
}
```

---

# 18. OperationalImpact

`OperationalImpact` translates Event and Scenario information into decision-support language.

```ts
interface OperationalImpact {
  id: string;

  eventId: string;
  scenarioRunId?: string;

  createdAt: string;

  headline: string;

  summary: string;

  implications: ImpactItem[];

  confidence: number;

  isSynthetic: boolean;
}
```

---

## ImpactItem

```ts
interface ImpactItem {
  id: string;

  category: string;

  statement: string;

  rationale: string;

  confidence: number;
}
```

Example:

```json
{
  "id": "IMPITEM-001",
  "category": "SCHEDULE_RELIABILITY",
  "statement": "Vessel arrival variability may increase.",
  "rationale": "Affected services may require longer alternative routes.",
  "confidence": 0.76
}
```

Operational impacts must use cautious wording such as:

```text
may
could
potential
possible
```

unless supported by observed data.

---

# 19. Recommendation

```ts
interface Recommendation {
  id: string;

  eventId: string;

  type: RecommendationType;

  title: string;
  description: string;

  rationale: string;

  priority: Severity;

  createdAt: string;

  isSynthetic: boolean;
}
```

---

## Monitor Example

```json
{
  "id": "REC-021",
  "eventId": "EVT-001",
  "type": "MONITOR",
  "title": "Monitor affected vessel ETAs",
  "description": "Track schedule changes for services associated with the affected corridor.",
  "rationale": "Rerouting may introduce additional schedule variability.",
  "priority": "HIGH",
  "createdAt": "2026-08-23T12:04:00Z",
  "isSynthetic": true
}
```

---

## Prepare Example

```json
{
  "id": "REC-022",
  "eventId": "EVT-001",
  "type": "PREPARE",
  "title": "Review contingency planning assumptions",
  "description": "Review plans that depend on stable vessel arrival schedules.",
  "rationale": "The current scenario indicates potential schedule variability.",
  "priority": "MEDIUM",
  "createdAt": "2026-08-23T12:04:00Z",
  "isSynthetic": true
}
```

---

# 20. ActivityLog

```ts
interface ActivityLog {
  id: string;

  timestamp: string;

  eventId?: string;
  articleId?: string;

  stage: ActivityStage;

  action: string;

  result?: string;

  status: ActivityStatus;

  metadata?: Record<string, unknown>;
}
```

Example:

```json
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
```

The Activity Log must not contain private chain-of-thought.

It may contain:

- actions performed
- structured reasons
- evidence references
- calculated results
- failures
- status changes

---

# 21. MaritimeRelevanceResult

This represents structured output from the maritime relevance step.

```ts
interface MaritimeRelevanceResult {
  maritimeRelevant: boolean;

  relevanceScore: number;

  reason: string;

  suggestedEventType?: EventType;

  potentialLocations: string[];
}
```

Example:

```json
{
  "maritimeRelevant": true,
  "relevanceScore": 0.93,
  "reason": "The article reports a security disruption affecting a major maritime chokepoint.",
  "suggestedEventType": "CHOKEPOINT_DISRUPTION",
  "potentialLocations": [
    "Bab el-Mandeb"
  ]
}
```

`relevanceScore` uses:

```text
0.00 – 1.00
```

---

# 22. EventExtractionResult

This is structured LLM output before an Event is created or updated.

```ts
interface EventExtractionResult {
  title: string;

  eventType: EventType;

  summary: string;

  locationName: string;

  eventTimestamp?: string;

  organisations: string[];

  possibleChokepoints: string[];

  possibleTradeCorridors: string[];

  evidenceClaims: ExtractedEvidenceClaim[];

  suggestedScenarioType?: ScenarioType;
}
```

---

## ExtractedEvidenceClaim

```ts
interface ExtractedEvidenceClaim {
  claim: string;

  sourceExcerpt?: string;
}
```

The Event extraction stage must not directly set:

- final confidence
- final severity
- final permissions
- scenario calculation results

Those are determined outside the LLM.

---

# 23. EventMatchSuggestion

```ts
interface EventMatchSuggestion {
  candidateEventId?: string;

  suggestedMatch: boolean;

  matchScore: number;

  reason: string;
}
```

The LLM may generate this suggestion.

The backend must apply deterministic thresholds before deciding whether the article updates an existing Event.

---

# 24. Data Relationships

Primary relationships:

```text
Article
   │
   ▼
Source
   │
   ├──────────────► Evidence
   │                    │
   │                    ▼
   └──────────────► Event
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   Development     ScenarioRun    Recommendation
                        │
                        ▼
                OperationalImpact
```

An Event may contain:

```text
1 Event
 ├── many Sources
 ├── many Evidence records
 ├── many Developments
 ├── many Scenario Runs
 ├── many Operational Impacts
 ├── many Recommendations
 └── many Activity Logs
```

---

# 25. Identifier Format

For readability during the hackathon, IDs may use prefixes.

Examples:

```text
ART-001
SRC-001
EVD-001
DEV-001
EVT-001
SCN-001
IMP-001
REC-001
LOG-001
```

The database may internally use UUIDs.

If UUIDs are used, the API should not depend on sequential IDs.

The implementation team should choose one approach before development starts.

---

# 26. Timestamp Format

All API timestamps should use ISO 8601.

Example:

```text
2026-08-23T12:05:22Z
```

Backend storage should use timezone-aware timestamps.

Frontend may convert timestamps to local display time.

---

# 27. Nullable and Unknown Values

Unknown information should be represented explicitly.

Do not invent values merely because a field exists.

Examples:

```json
{
  "url": null
}
```

or:

```json
{
  "routeExposure": null
}
```

The frontend should handle unresolved values gracefully.

Example:

```text
Route exposure:
Under assessment
```

instead of fabricating a route.

---

# 28. Data Validation Rules

The following rules should be enforced.

## Confidence

```text
0.0 <= confidence <= 1.0
```

---

## Relevance Score

```text
0.0 <= relevanceScore <= 1.0
```

---

## Scenario Range

If:

```text
minValue
maxValue
```

are both present:

```text
minValue <= maxValue
```

---

## Synthetic Data

If data is fabricated for demonstration:

```text
isSynthetic = true
```

or:

```text
sourceType = SYNTHETIC_DEMO_DATA
```

as appropriate.

---

## Event Dates

```text
firstSeen <= lastUpdated
```

---

## Development Dates

A Development should normally not predate its parent Event's `firstSeen`.

---

# 29. Database Mapping

The backend may normalize the models into relational tables.

Suggested tables:

```text
articles
events
sources
event_sources
evidence
developments
chokepoints
scenario_runs
scenario_assumptions
scenario_metrics
operational_impacts
impact_items
recommendations
activity_logs
```

The exact SQL schema may differ from the API representation.

The API/domain model defined in this document remains the shared contract.

---

# 30. MVP Data Boundary

For the initial MVP, do not introduce additional domain objects unless necessary.

Avoid prematurely modelling:

- individual containers
- cranes
- yard blocks
- prime movers
- detailed vessel manifests
- PSA manpower
- terminal allocation systems

These belong outside the Global Watch MVP.

---

# 31. Contract Change Rule

Once implementation begins, shared model changes must follow this process:

```text
Proposed model change
       │
       ▼
Update DATA_SPEC.md
       │
       ▼
Team agreement
       │
       ▼
Backend model updated
       │
       ▼
API contract updated if required
       │
       ▼
Frontend/types updated
```

A developer should not silently add or rename shared fields.

---

# 32. Definition of Data Contract Success

The data specification is successful when all four development areas can answer:

> What object do I send or receive?

without inventing their own representation.

The following objects should be considered stable enough for MVP implementation:

- Article
- Event
- Source
- Evidence
- Development
- Location
- Chokepoint
- RouteExposure
- ScenarioAssumption
- ScenarioInput
- ScenarioMetric
- ScenarioRun
- OperationalImpact
- ImpactItem
- Recommendation
- ActivityLog
- MaritimeRelevanceResult
- EventExtractionResult
- EventMatchSuggestion