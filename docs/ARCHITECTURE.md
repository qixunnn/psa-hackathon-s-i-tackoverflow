# Architecture

**Project:** PSA Global Watch  
**Version:** 1.0

---

# 1. Architecture Goal

PSA Global Watch is designed as a lightweight three-agent decision-support platform that transforms global maritime disruptions into structured operational intelligence.

The architecture must support the following agentic workflow:

```text
External Event
      │
      ▼
Global Watch Agent
      │
      ▼
Persistent Event Memory
      │
      ▼
Scenario & Risk Agent
      │
      ▼
Deterministic Scenario Engine
      │
      ▼
Advisory Agent
      │
      ▼
Potential PSA Impact + Monitor / Prepare
```

The system is designed for hackathon delivery first.

It should remain modular enough for future expansion, but implementation complexity must not exceed what is required for the MVP.

---

# 2. Architecture Principles

## 2.1 LLM Interprets, Deterministic Code Calculates

The most important architectural rule is:

> **LLM interprets. Deterministic code calculates.**

The LLM is used for tasks involving unstructured information and language understanding.

Examples:

- maritime relevance classification
- structured event extraction
- evidence extraction
- event-match suggestions
- disruption-type classification
- scenario-template selection
- operational explanation
- Monitor / Prepare recommendation generation

Deterministic application logic is responsible for:

- schema validation
- event persistence
- duplicate handling
- confidence rules
- risk thresholds
- scenario calculations
- Monte Carlo simulation
- authorization logic
- API behaviour

The LLM must not invent mathematical models or control system permissions.

---

## 2.2 Persistent Events, Not Independent Articles

News articles are treated as evidence about an Event.

The system does not treat every article as an isolated alert.

Example:

```text
Article 1
Security incident reported
       │
       ▼
EVT-001 created
       │
Article 2
Independent confirmation
       │
       ▼
EVT-001 updated
       │
Article 3
Carrier announces rerouting
       │
       ▼
EVT-001 updated
```

This creates persistent event intelligence and allows users to understand how a disruption develops over time.

---

## 2.3 Evidence Before Interpretation

Operational conclusions must remain traceable to:

- source articles
- extracted evidence
- known maritime-route relationships
- explicit scenario assumptions
- deterministic model outputs

The UI should clearly distinguish between:

- observed evidence
- extracted facts
- assumptions
- calculated outputs
- AI-generated interpretation

---

## 2.4 Human Decision Support

The MVP does not autonomously control port operations.

The system provides:

- awareness
- scenario analysis
- potential operational implications
- Monitor recommendations
- Prepare recommendations

Operational decisions remain with human users.

---

## 2.5 Three-Agent Boundary

The MVP uses three AI agents with clearly separated responsibilities.

### Global Watch Agent

Responsible for understanding new external information and maintaining the system's evolving view of a maritime disruption.

Responsibilities include:

- maritime relevance classification
- structured event extraction
- evidence extraction
- event-match suggestion
- event update suggestions

The Global Watch Agent reads and interprets information. Deterministic application logic validates its output and decides whether an Event is created or updated.

### Scenario & Risk Agent

Responsible for deciding how an Event should be analysed using the system's maritime knowledge and predefined analytical tools.

Responsibilities include:

- interpreting route and chokepoint context
- selecting an appropriate predefined scenario template
- identifying required scenario parameters from validated evidence
- interpreting deterministic scenario outputs
- producing a structured risk assessment

The Scenario & Risk Agent does not invent mathematical models or calculate simulation results itself.

### Advisory Agent

Responsible for converting validated Event state and scenario results into PSA-facing decision support.

Responsibilities include:

- summarising potential operational implications
- generating Monitor recommendations
- generating Prepare recommendations
- explaining why the recommendations follow from the available evidence and model outputs

The Advisory Agent remains advisory and cannot execute operational actions.

The three agents share persistent Event state through the backend and database rather than through hidden conversational memory.

---

# 3. High-Level Architecture

```text
┌───────────────────────────────────────┐
│          External Data Sources        │
│                                       │
│  Replay Dataset / RSS / News APIs     │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│            Ingestion Layer            │
│                                       │
│  • normalize article                  │
│  • validate source                    │
│  • deduplicate article                │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│          Global Watch Agent           │
│                                       │
│  • maritime relevance                │
│  • structured extraction             │
│  • evidence extraction               │
│  • event-match suggestion            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│          Event Intelligence           │
│                                       │
│  • persistent Event                   │
│  • sources                            │
│  • evidence                           │
│  • developments                       │
│  • confidence                         │
│  • severity                           │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│      Maritime Knowledge Layer         │
│                                       │
│  • chokepoints                        │
│  • trade corridors                    │
│  • route relationships                │
│  • scenario mappings                  │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│        Scenario & Risk Agent          │
│                                       │
│  • interpret route exposure          │
│  • select scenario template          │
│  • prepare validated parameters      │
│  • interpret model outputs           │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│          Scenario Engine              │
│                                       │
│  • predefined scenario templates      │
│  • validated assumptions              │
│  • deterministic calculations         │
│  • Monte Carlo where appropriate      │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│            Advisory Agent             │
│                                       │
│  • potential PSA relevance            │
│  • Monitor recommendations            │
│  • Prepare recommendations            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│               API Layer               │
│             FastAPI / REST            │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│               Frontend                │
│                                       │
│  • Global Risk Overview               │
│  • Event Detail                       │
│  • Scenario Lab                       │
│  • Activity Log                       │
└───────────────────────────────────────┘
```

---

# 4. Technology Architecture

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- MapLibre or Mapbox for geospatial display

Responsibilities:

- display tracked Events
- display event severity and confidence
- show Event Evolution timeline
- show evidence and sources
- show route exposure
- show scenario assumptions and outputs
- show Monitor / Prepare recommendations
- display Activity Log

The frontend should not contain business-critical calculation logic.

---

## Backend

- FastAPI
- Python
- Pydantic

Responsibilities:

- expose REST endpoints
- validate API input/output
- orchestrate event-processing workflows
- call AI services
- interact with Supabase
- run scenario models
- enforce deterministic rules
- write Activity Log records

---

## Database

- Supabase PostgreSQL

Primary persisted entities include:

- Events
- Sources
- Evidence
- Developments
- Scenario Runs
- Operational Impacts
- Recommendations
- Activity Logs

Detailed schemas are defined in `DATA_SPEC.md`.

---

## AI Provider

- OpenAI API

AI calls should return structured output that can be validated before use.

Free-form LLM text must not be written directly into critical system state without validation.

---

## Simulation

- Python
- NumPy

Scenario calculations should use predefined deterministic scenario templates.

Monte Carlo simulation may be used where useful, but outputs must be presented as conditional simulation results rather than validated predictions.

---

# 5. Ingestion Layer

The ingestion layer converts different input sources into a canonical article format.

Initial MVP input:

- replayed JSON demo articles

Possible later input:

- RSS feeds
- news APIs
- maritime bulletins
- public carrier announcements

All inputs must be normalized before entering the intelligence pipeline.

Canonical flow:

```text
Raw input
    │
    ▼
Normalize
    │
    ▼
Validate
    │
    ▼
Article deduplication
    │
    ▼
Processing pipeline
```

A live-data source must not require a separate intelligence pipeline.

Replay and live sources should feed the same processing path.

---

# 6. Agentic Intelligence Pipeline

The three-agent pipeline is the core of the system.

```text
Article
   │
   ▼
GLOBAL WATCH AGENT
   │
   ├─ Maritime Relevance
   │
   ├── irrelevant → stop
   │
   ├─ Structured Event Extraction
   ├─ Evidence Extraction
   └─ Existing Event Match
   │
   ├── existing → update Event
   │
   └── new      → create Event
   │
   ▼
PERSISTENT EVENT MEMORY
   │
   ▼
SCENARIO & RISK AGENT
   │
   ├─ Route / Chokepoint Context
   └─ Scenario Template Selection
   │
   ▼
DETERMINISTIC SCENARIO ENGINE
   │
   ▼
ADVISORY AGENT
   │
   ├─ Operational Impact
   └─ Monitor / Prepare
```

Each major stage should create an Activity Log entry.

---

# 7. Maritime Relevance

The first intelligence step determines whether an article is relevant to maritime operations.

Inputs may include:

- title
- article text
- source
- publication time

Output should be structured.

Example fields:

```text
maritime_relevant
relevance_score
reason
event_type
potential_locations
```

Irrelevant articles should stop here and should not create Events.

---

# 8. Event Extraction

For maritime-relevant articles, the LLM extracts structured facts.

Examples:

- disruption type
- location
- affected chokepoint
- organisations/carriers involved
- event date
- extracted evidence
- possible affected routes

The output is validated using Pydantic.

Invalid output should trigger:

1. structured retry where appropriate
2. failure logging
3. graceful termination if still invalid

The system must never silently accept malformed LLM output.

---

# 9. Event Matching and Event Evolution

The system should determine whether a new article relates to an existing Event.

Matching may use:

- event type
- location
- chokepoint
- entities
- time proximity
- semantic similarity
- LLM match suggestion

The LLM may recommend a match, but deterministic code decides whether the match satisfies configured thresholds.

Possible outcomes:

```text
New article
    │
    ▼
Candidate Event matches
    │
    ├── strong match
    │      ▼
    │   update Event
    │
    ├── ambiguous
    │      ▼
    │   flag / use fallback rule
    │
    └── no match
           ▼
        create Event
```

Each update creates a Development entry.

This forms the Event Evolution timeline.

---

# 10. Confidence and Severity

Confidence and severity represent different concepts.

## Confidence

Represents how strongly available evidence supports the current event assessment.

Factors may include:

- number of independent sources
- source quality
- consistency between sources
- direct carrier or authority confirmation

Confidence should be computed using deterministic rules where practical.

The LLM must not freely assign final confidence.

---

## Severity

Represents the potential significance of the disruption.

Severity may use an enum such as:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Severity may consider:

- chokepoint importance
- event type
- affected route exposure
- confirmed rerouting
- disruption duration
- scale of affected traffic

The exact calculation belongs in deterministic application logic.

---

# 11. Maritime Knowledge Layer

The system should maintain a curated maritime knowledge dataset.

Initial MVP should focus only on important locations.

Examples:

- Bab el-Mandeb
- Suez Canal
- Strait of Hormuz
- Strait of Malacca
- Panama Canal

Each chokepoint may store:

- name
- region
- coordinates
- connected sea regions
- major trade corridors
- known alternative routes
- supported scenario types

Example relationship:

```text
Bab el-Mandeb
      │
      ├── Asia-Europe corridor
      │
      ├── Red Sea
      │
      └── alternative:
             Cape of Good Hope
```

The MVP does not require a full global shipping network graph.

---

# 12. Scenario & Risk Agent and Scenario Engine

The Scenario & Risk Agent decides which predefined analytical tool is appropriate for an Event and prepares validated inputs. The Scenario Engine then performs the transparent what-if analysis.

The Scenario & Risk Agent may select a predefined scenario template.

It must not generate the mathematical model.

Initial scenario templates may include:

```text
CarrierReroutingScenario
ChokepointDisruptionScenario
CanalClosureScenario
PortStrikeScenario
SevereWeatherScenario
TradeRestrictionScenario
```

Each scenario contains:

- required inputs
- optional inputs
- default assumptions
- assumption sources
- deterministic calculation logic
- output schema

---

# 13. Scenario Assumptions

Every assumption must have provenance.

An assumption should record:

```text
name
value or range
unit
reason
source type
source reference
```

Source types may include:

```text
EXTERNAL_SOURCE
SYSTEM_CONFIG
AI_EXTRACTION
USER_INPUT
SYNTHETIC_DEMO_DATA
```

Example:

```text
Carrier rerouting share
Range: 40–70%
Source type: SYNTHETIC_DEMO_DATA
Reason: Demonstration scenario assumption
```

The UI must not hide assumptions from users.

---

# 14. Scenario Outputs

Scenario outputs should contain both quantitative and qualitative results.

Example:

```text
Simulation runs: 10,000

Median additional sailing time:
10.8 days

80% simulation interval:
8.6–13.1 days

61% of simulated outcomes exceed
the configured arrival-variability threshold.
```

Correct language:

> Under the current scenario assumptions, 61% of simulated outcomes exceed the configured threshold.

Incorrect language:

> There is a 61% chance PSA will experience disruption.

---

# 15. Advisory Agent

The Advisory Agent translates validated Event state and deterministic scenario outputs into potential operational implications.

Examples:

- increased vessel arrival variability
- potential changes in schedule reliability
- possible transshipment-connection pressure
- increased monitoring priority

The platform should avoid unsupported operational precision.

If the system does not possess real PSA operational data, it must not claim specific:

- berth allocations
- yard-block utilisation
- manpower requirements
- equipment movements

Synthetic operational data must be clearly labelled.

---

# 16. Monitor and Prepare

Recommendations are separated into two categories.

## Monitor

Signals that should continue to be observed.

Examples:

- vessel ETA changes
- carrier route announcements
- additional source confirmation
- chokepoint status
- schedule reliability indicators

## Prepare

Possible planning considerations.

Examples:

- review contingency capacity
- review affected transshipment flows
- review assumptions used in operational plans
- prepare for possible schedule variability

Prepare recommendations remain advisory.

---

# 17. Activity Log

The Activity Log is a first-class system component.

Its purpose is to expose system actions without exposing hidden chain-of-thought.

Example:

```text
23:10:01 Article ingested
23:10:02 Maritime relevance: HIGH
23:10:04 Existing event matched: EVT-001
23:10:05 New independent source added
23:10:06 Confidence updated: 0.71 → 0.84
23:10:08 Route exposure identified
23:10:09 Scenario executed
23:10:10 Advisory refreshed
```

The Activity Log should capture:

- stage
- responsible agent
- timestamp
- event ID where applicable
- action
- concise result
- success/failure status

It should make the multi-agent handoff visible without exposing private chain-of-thought. A typical sequence is:

```text
Global Watch Agent
  Observe → Interpret → Verify
                 ↓
Scenario & Risk Agent
  Model → Assess
                 ↓
Advisory Agent
  Recommend
```

---

# 18. Frontend Information Architecture

The MVP frontend should contain four primary views.

## 18.1 Global Risk Overview

Displays:

- active Events
- world map
- severity
- confidence
- location
- affected route/chokepoint
- last update

---

## 18.2 Event Detail

Displays:

- what happened
- Event Evolution
- evidence
- sources
- Route Exposure
- scenario summary
- potential PSA impact
- Monitor
- Prepare

---

## 18.3 Scenario Lab

Displays:

- scenario type
- assumptions
- assumption provenance
- adjustable inputs where supported
- deterministic model results
- uncertainty
- interpretation

---

## 18.4 Activity Log

Displays processing activity and event updates.

---

# 19. Failure Handling

The system should fail visibly and safely.

Examples:

## LLM unavailable

- log failure
- keep existing Event state
- surface processing failure
- allow retry

## Invalid structured output

- validate with Pydantic
- retry once if appropriate
- reject invalid result if validation still fails

## No matching scenario

- Event remains valid
- show that scenario analysis is unavailable
- do not fabricate one

## No route match

- retain Event
- flag route exposure as unresolved
- avoid unsupported PSA-impact claims

## Database failure

- return controlled API error
- log failure where possible

---

# 20. Security Boundaries

Secrets such as API keys must remain server-side.

Never expose:

- OpenAI API keys
- Supabase service-role keys
- private credentials

Frontend access should use only public-safe configuration.

No secrets should be committed to Git.

---

# 21. MVP Architecture Boundary

The following are explicitly outside the core MVP architecture:

- full terminal digital twin
- crane optimisation
- prime-mover optimisation
- autonomous terminal control
- production-grade AIS ingestion
- large-scale global route graph
- advanced geopolitical forecasting

These may be explored only after the MUST scope works end to end.

---

# 22. Optional Downstream Terminal Demonstration

If time permits, one synthetic downstream terminal scenario may be connected to the intelligence platform.

Example:

```text
Global disruption
      │
      ▼
Scenario indicates increased arrival variability
      │
      ▼
Synthetic terminal environment fast-forwards
      │
      ▼
Synthetic yard pressure increases
      │
      ▼
Terminal recommendation generated
```

All operational data used in this demonstration must be explicitly marked:

> **Synthetic demonstration data**

This feature should not be required for the Global Watch MVP to be considered complete.

---

# 23. End-to-End MVP Sequence

The target end-to-end architecture is:

```text
Replay article
      │
      ▼
Normalize article
      │
      ▼
Global Watch Agent checks maritime relevance
      │
      ▼
Extract structured facts
      │
      ▼
Validate output
      │
      ▼
Create or update Event
      │
      ▼
Update evidence + timeline
      │
      ▼
Persist / update Event memory
      │
      ▼
Scenario & Risk Agent resolves route exposure
      │
      ▼
Select predefined scenario
      │
      ▼
Run deterministic scenario engine
      │
      ▼
Advisory Agent generates operational interpretation
      │
      ▼
Generate Monitor / Prepare
      │
      ▼
Persist results
      │
      ▼
Update dashboard
      │
      ▼
Record Activity Log
```

---

# 24. Definition of Architecture Success

The architecture is considered successful when four developers can independently work on:

1. Global Watch / AI
2. Backend / Data
3. Scenario / Risk
4. Frontend

without inventing incompatible representations of the same system.

Shared contracts are defined in:

- `PRODUCT_SPEC.md`
- `DATA_SPEC.md`
- `API_SPEC.md`

Implementation should conform to these documents rather than redefining behaviour independently.