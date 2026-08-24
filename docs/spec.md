# PSA Sentinel — Agentic Supply Chain Risk Advisory System
### Spec — PSA Code Sprint 2.0

---

## 1. Product Summary

PSA Sentinel is an agentic AI system that monitors real-world events (starting
with a single news article as input) and reasons about whether that event
threatens the on-time arrival of vessels bound for PSA (Port of Singapore
Authority). A pipeline of specialized agents extracts the event, assesses its
severity and geographic relevance, retrieves alternative shipping routes from
a pre-built route graph, ranks those routes by likelihood and estimated time
of arrival (ETA) impact, and finally produces a human-readable advisory —
displayed on a live operations dashboard — that tells a PSA planner what is
likely to happen and what to do about it.

The system is **advisory / human-in-the-loop by design**: it never re-routes
a vessel automatically. It surfaces reasoning, evidence, and ranked options so
a human operator makes the final call. This keeps the MVP scoped, auditable,
and safe to demo — while leaving a clear extension path toward
higher-autonomy execution (e.g., auto-notifying a shipping line) in future
iterations.

**Why this matters for PSA:** Port operations run on tight berth, crane, and
labour scheduling. A vessel arriving days late or early because of a
geopolitical/weather/logistics disruption cascades into berth congestion,
missed transshipment windows, and customer SLA breaches. Early, well-reasoned
warning — even a few days' notice — has outsized operational and cost value
relative to the effort of reading and triaging global news manually.

---

## 2. Product Goals

| # | Goal | Success Signal (MVP) |
|---|------|------------------------|
| G1 | Detect PSA-relevant disruption events from unstructured news input | Correctly classifies relevant vs. irrelevant articles |
| G2 | Quantify severity/risk consistently and explainably | Structured risk JSON with rationale, not just a label |
| G3 | Recommend feasible alternative routes, not hypothetical ones | Routes returned always exist in the pre-generated route graph |
| G4 | Estimate schedule impact (ETA delta) per route | Ranked routes with delay/advance estimates |
| G5 | Give PSA planners a clear, actionable advisory | One-paragraph advisory + structured "recommended actions" list |
| G6 | Keep a human in the loop | Every AI output is a recommendation the operator can accept/reject/edit |

**Explicit non-goals for MVP:** automatic re-routing, multi-article
correlation, real-time AIS vessel tracking, multi-port support beyond PSA,
real-time re-scraping/polling of news feeds (MVP is triggered by manual URL
submission).

---

## 3. Users

| User | Need | How Sentinel Helps |
|------|------|---------------------|
| **Port Operations Planner** | Early warning of inbound schedule risk to plan berth/crane/labour allocation | Dashboard advisory + ranked routes + ETA deltas |
| **Trade & Supply Chain Risk Analyst** | Evidence-backed risk assessment they can escalate internally | Structured JSON audit trail, severity scoring, source citation |
| **Duty Manager / Crisis Response Team** | Fast situational awareness during an active crisis (e.g. strait closure) | Live event log, scenario overlay, "what changed" summary |
| **Hackathon Judges (secondary)** | Understand agentic reasoning, orchestration, and business impact | Visible agent pipeline status, explainable intermediate JSON, architecture clarity |

---

## 4. Interface

The UI is a single-page **operations dashboard** (reference: 2D maritime map
view, right-hand agent activity rail, bottom event log — see attached
reference mockup) plus one **input surface** for the MVP trigger.

### 4.1 Dashboard (Home)
- **Map panel** — the single pre-defined MVP route (origin → PSA Singapore)
  rendered on a 2D map, with the active/affected chokepoint highlighted
  (e.g. Strait of Hormuz) when a live risk exists.
- **Route comparison panel** — once an advisory exists, shows the current
  scheduled route vs. top-ranked alternative(s), each with: distance, transit
  days, ETA, delta vs. original ETA, risk exposure summary.
- **Advisory card** — plain-language summary + confidence + recommended
  action(s) + "Accept / Dismiss / Request more detail" controls for the
  human operator.
- **Agent pipeline status rail** — live status of each of the 5 agents
  (queued → running → done / error), mirroring the reference UI's "Google
  Gemini / Google AI Search / Google Cognitive" style status cards. This
  gives visibility into orchestration for both operators and judges.
- **System event log** — timestamped log of pipeline actions
  ("Article ingested", "Relevance confirmed", "Risk severity: HIGH",
  "3 alternative routes retrieved", "Advisory generated") for auditability.
- **Risk trend strip** — small time-series of risk score for the active
  route over recent runs (supports "is this getting worse" at a glance).

### 4.2 Input: Article URL Submission
- Single text field: paste an article URL.
- Optional: user note/context (e.g., "flagged by ops team").
- Submit → triggers the agent pipeline; UI shows the pipeline rail
  transitioning through each agent in real time (via polling or streamed
  status updates).
- On completion: dashboard auto-updates with advisory + routes; if the
  article is judged **not relevant**, the UI shows a short "No PSA impact
  detected" state with the extracted reasoning (not a silent failure — this
  is itself valuable, auditable output).

### 4.3 Additional supporting interfaces (recommended additions)
- **History / Past Runs list** — table of all past article submissions with
  outcome (relevant/not), severity, advisory status (accepted/dismissed),
  timestamp — supports the "auditability" evaluation criterion.
- **Route Graph Viewer (read-only, admin)** — visualizes the pre-generated
  route graph for the MVP origin→PSA corridor, so judges/operators can see
  what alternatives the Route Retrieval Agent is allowed to choose from.
  Not editable in MVP.
- **Human Decision Panel** — explicit accept/override control on the
  Advisory card; decision + optional operator comment is persisted, closing
  the human-in-the-loop feedback loop and giving a dataset for future
  fine-tuning/evaluation.

---

## 5. AI Requirements

### 5.1 Design principles
- Each agent has **one responsibility** and a **strict input/output
  contract** (JSON in, JSON out) — easier to test, log, and swap models for.
- State is **persisted after every agent step** (not just at the end), so a
  failure mid-pipeline doesn't lose prior work and each step is independently
  auditable/replayable.
- Every agent must **cite its evidence** (source article excerpt, route
  graph edge ID, etc.) — no unsupported claims reach the advisory.
- A **confidence score** accompanies relevance, severity, and ranking
  outputs so low-confidence results can be flagged for human review rather
  than silently trusted.

### 5.2 Agentic Pipeline (5 agents, sequential with shared state object)

**Agent 1 — Relevance & Extraction Agent**
- Input: article URL.
- Actions: fetch/scrape article content (tool: web scraper/fetcher);
  summarize; classify relevance to PSA-bound shipping (binary + confidence +
  rationale); extract structured entities (location, event type, date,
  actors involved, chokepoints/waterways mentioned).
- Output: `event.json` — `{ relevant: bool, confidence, summary,
  entities: {...}, source_url, extracted_at }`.
- If `relevant = false`: pipeline halts here; result surfaced to UI as-is
  (with rationale) — this is a valid terminal state, not an error.

**Agent 2 — Risk & Severity Assessment Agent**
- Input: `event.json`.
- Actions: assess severity (e.g. Low/Medium/High/Critical), estimate
  probability the event materially disrupts transit, identify which
  chokepoint(s)/route segment(s) are affected, estimate plausible disruption
  duration.
- Output: appends `risk_assessment` block to the same JSON —
  `{ severity, probability, affected_chokepoints: [...], estimated_duration,
  rationale }`.

**Agent 3 — Route Retrieval Agent**
- Input: `event.json` (with risk block) + reference to **pre-generated route
  graph** (static dataset built ahead of time for the MVP corridor).
- Actions: query the route graph for the affected chokepoint(s); retrieve
  all viable alternative paths from origin to PSA that avoid or mitigate the
  affected segment; retrieve baseline/original route data for comparison.
- Output: appends `candidate_routes: [...]` — each with route ID, waypoints,
  distance (nm), avg. transit days, chokepoints traversed.
- **No LLM route invention** — this agent is constrained to graph lookups
  only, to guarantee geographic feasibility (important for reliability and
  judge trust).

**Agent 4 — Ranking & Impact Aggregation Agent**
- Input: `candidate_routes` + `risk_assessment`.
- Actions: rank candidate routes by a weighted score (risk exposure, transit
  time, distance/cost proxy); compute ETA and ETA-delta vs. scheduled arrival
  for the top route(s); aggregate overall PSA operational impact (e.g.,
  "vessel X likely arrives 3–5 days late").
- Output: appends `ranked_routes: [...]` with `rank, score, eta,
  eta_delta_days, rationale`.

**Agent 5 — Advisory & Recommendation Agent**
- Input: full accumulated JSON (event + risk + ranked routes).
- Actions: synthesize a plain-language advisory for a PSA operator; generate
  concrete recommended actions (e.g., "flag berth slot for possible 4-day
  delay", "notify transshipment partners", "monitor — no action needed yet").
- Output: appends `advisory: { headline, summary, recommended_actions: [...],
  confidence }` — this is what renders on the dashboard.

### 5.3 Orchestration & State Management
- A lightweight **orchestrator** (sequential state machine, not a free-form
  agent loop) calls agents 1→5 in order, persisting the shared JSON object to
  storage after each step (`run_id` keyed).
- Orchestrator enforces the contract: each agent's output is validated
  against a JSON schema before being passed to the next agent; a schema
  failure halts the run and surfaces an error state rather than passing
  malformed data downstream.
- Pipeline run state: `queued → extracting → assessing_risk →
  retrieving_routes → ranking → advising → complete | halted_not_relevant |
  error`.

### 5.4 Human-in-the-loop checkpoints
- Terminal advisory always requires explicit operator **Accept/Dismiss**
  before being treated as "actioned" in the history log.
- Low-confidence outputs (below a configurable threshold) are visually
  flagged for mandatory human review rather than auto-surfaced as fact.

---

## 6. Core Data Entities

| Entity | Key Fields | Notes |
|--------|-----------|-------|
| **Run** | `run_id`, `status`, `submitted_by`, `submitted_at`, `source_url` | Top-level record per article submission |
| **Event** | `run_id`, `relevant`, `confidence`, `summary`, `entities{}` | Output of Agent 1 |
| **RiskAssessment** | `run_id`, `severity`, `probability`, `affected_chokepoints[]`, `estimated_duration`, `rationale` | Output of Agent 2 |
| **Route** (graph node/edge) | `route_id`, `origin`, `destination`, `waypoints[]`, `chokepoints[]`, `distance_nm`, `base_transit_days` | Pre-generated, static for MVP |
| **CandidateRoute** | `run_id`, `route_id`, `retrieved_reason` | Output of Agent 3, references Route |
| **RankedRoute** | `run_id`, `route_id`, `rank`, `score`, `eta`, `eta_delta_days`, `rationale` | Output of Agent 4 |
| **Advisory** | `run_id`, `headline`, `summary`, `recommended_actions[]`, `confidence`, `operator_decision`, `operator_comment` | Output of Agent 5 + human decision |
| **Vessel** (MVP-lite) | `vessel_name`, `scheduled_route_id`, `scheduled_arrival` | Static/mocked for demo — one vessel on the MVP route |
| **EventLogEntry** | `run_id`, `timestamp`, `agent`, `message` | Powers the System Event Log UI |

---

## 7. Integrations

- **LLM: Google Gemini** — used for Agents 1, 2, 4 (partial), and 5
  (extraction, classification, severity reasoning, ranking rationale,
  advisory synthesis). Agent 3 (route retrieval) is deliberately **not**
  LLM-driven — it's a deterministic graph query — to guarantee feasibility
  and reduce hallucination risk and token cost.
- **Web content fetching/scraping tool** — retrieves article HTML/text for
  Agent 1 (e.g., a fetch + readability-extraction utility). Should handle
  paywalled/failed fetches gracefully (fallback: use URL metadata / ask
  operator to paste text).
- **Optional: Gemini grounding / search tool** — could supplement Agent 2
  with corroborating context (e.g., "is this event still ongoing?"). Marked
  optional/stretch for MVP to control scope and cost.
- **Pre-generated Route Graph store** — a static dataset a
  small graph DB built ahead of the hackathon demo, representing known
  shipping lanes, chokepoints, and alternative paths for the single MVP
  corridor. This is **not** generated live by AI — it's reference data the
  agents query, similar in spirit to the "Shipping Routes / Major Ports"
  reference data shown in the mockup UI.
- **Persistence layer** — stores Run/Event/Risk/Route/Advisory records for
  the History and Drill-down views (e.g., a lightweight database or even
  structured JSON files for MVP speed).

---

## 8. MVP Scope

**Single corridor, single live-risk scenario, single vessel.**

- **Route (MVP demo corridor):** Rotterdam (or Jebel Ali) → PSA Singapore.
- **Primary demo scenario: Strait of Hormuz Tension** — matches a real,
  well-known chokepoint risk (also aligns with the "Hormuz Tension" scenario
  category visible in the reference dashboard UI, alongside Red Sea Crisis,
  Suez, Taiwan Strait). A tension/closure event at Hormuz is used as the
  scripted demo input article.
- **Pre-generated route graph** for this MVP corridor includes at least:
  1. Baseline route (via the affected chokepoint).
  2. 1–2 realistic alternative routes (e.g., re-routing around the
     chokepoint or via an alternate strait/cape), each with distance and
     transit-day estimates pre-computed.
- **One mocked vessel** with a scheduled arrival, to make the "ETA delta"
  and PSA operational impact concrete and demoable.
- **One article input path**: manual URL paste (no live news polling/feed
  ingestion in MVP).
- **Out of scope for MVP:** multiple concurrent routes/corridors, real AIS
  vessel tracking integration, autonomous re-routing/booking actions,
  multi-article correlation over time, user auth/roles (single operator
  view is fine for demo).

**Demo narrative:** operator pastes a news article about rising Strait of
Hormuz tensions → pipeline runs end-to-end in view (agent rail lights up
sequentially) → dashboard shows the corridor's chokepoint flagged, 2 ranked
alternative routes with ETA deltas, and an advisory recommending PSA flag a
possible multi-day delay and notify transshipment partners → operator clicks
Accept, decision logged.

---

## 9. Technology Stack

| Layer | Suggested Choice | Notes |
|-------|-------------------|-------|
| LLM | Google Gemini (via API) | Per requirement; used for reasoning agents |
| Backend / Orchestration | Python (FastAPI) | Orchestrator + agent runner + REST endpoints |
| Agent framework | Lightweight custom orchestrator (sequential state machine) | Keep it simple/inspectable for judging; avoid opaque multi-agent frameworks for MVP |
| Article scraping | `readability`/`trafilatura`-style extractor or headless fetch | Fallback to manual paste on failure |
| Route graph storage | JSON file | Pre-generated ahead of demo, static for MVP |
| Persistence |  JSON files for speed | Runs, events, advisories, history |
| Frontend | React (+ Tailwind), map via a lightweight 2D map/SVG layer (e.g., Mapbox GL, deck.gl, or a simplified custom SVG map) | Matches reference dashboard aesthetic |
| Realtime pipeline status | SSE | Drives the agent pipeline status rail |
| Hosting (demo) | Vercel/Render + Cloud Run | Optimize for reliable live demo, not production scale |

---

## 10. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend Dashboard                         │
│  Map + Route Panel | Agent Status Rail | Advisory Card | Event Log  │
│  Article URL Input | History / Drill-down | Human Decision Panel    │
└───────────────────────────────┬───────────────────────────────────┘
                                 │ REST / SSE (poll pipeline status)
┌───────────────────────────────▼───────────────────────────────────┐
│                          Orchestrator / API                        │
│   Validates schema per step · persists state · sequences agents    │
└───────────────────────────────┬───────────────────────────────────┘
      │              │              │               │              │
      ▼              ▼              ▼               ▼              ▼
 ┌─────────┐   ┌───────────┐  ┌───────────┐  ┌────────────┐  ┌───────────┐
 │ Agent 1 │   │  Agent 2  │  │  Agent 3  │  │  Agent 4   │  │  Agent 5  │
 │Relevance│──▶│   Risk /  │─▶│  Route    │─▶│  Ranking / │─▶│ Advisory /│
 │& Extract│   │ Severity  │  │ Retrieval │  │   Impact   │  │  Recomm.  │
 │(Gemini) │   │ (Gemini)  │  │(Graph DB, │  │ (Gemini +  │  │ (Gemini)  │
 │+ scraper│   │           │  │ no LLM)   │  │ scoring)   │  │           │
 └─────────┘   └───────────┘  └─────┬─────┘  └────────────┘  └───────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────┐
                     │  Pre-generated Route Graph      │
                     │  (static, built ahead of demo)  │
                     │  origin ↔ PSA, chokepoints,     │
                     │  alt paths, distances, transit  │
                     └───────────────────────────────┘

                     ┌───────────────────────────────┐
                     │   Persistence: Runs, Events,     │
                     │   Risk, Routes, Advisories,      │
                     │   Operator Decisions (audit log) │
                     └───────────────────────────────┘
```

**Key architectural decisions:**
- **Sequential, schema-validated pipeline** over a free-form multi-agent
  loop — prioritizes reliability and auditability (per evaluation criteria)
  over open-ended autonomy, consistent with the brief's note that "higher
  autonomy is not automatically better."
- **Route retrieval is deterministic, not generative** — the LLM reasons
  about *risk*, not about *geography*, which it isn't well-suited to
  invent reliably.
- **State persisted at every step** — enables the Drill-down/History views,
  supports auditability, and means a downstream agent failure doesn't
  discard upstream work.
- **Human decision is a first-class data point**, not an afterthought —
  captured and logged, supporting both responsible-AI governance and future
  model evaluation/fine-tuning.

---

## 11. Responsible AI, Security & Scalability Notes

- **Guardrails:** relevance/severity/ranking outputs include confidence
  scores; low-confidence results are flagged for mandatory human review
  before being treated as actionable.
- **No autonomous action:** system only recommends; all consequential
  actions (route changes, partner notifications) require explicit operator
  acceptance — appropriate given the reputational/financial cost of a wrong
  autonomous port-ops decision.
- **Auditability:** every run retains full lineage (source article → each
  agent's JSON output → final advisory → human decision), satisfying the
  evaluation criterion on auditability.
- **Error handling:** malformed agent output halts the pipeline at that
  step rather than propagating bad data; scraping failures degrade
  gracefully (prompt for manual text paste) rather than crashing the run.
- **Cost/token efficiency:** Agent 3 avoids LLM calls entirely (deterministic
  graph lookup); prompts for Agents 1/2/4/5 are scoped narrowly per-step
  rather than one large multi-purpose prompt, keeping token usage
  predictable and easier to budget/monitor.
- **Scalability path (post-MVP):** the same 5-agent contract generalizes to
  (a) multiple corridors by scaling the route graph, (b) multiple concurrent
  articles/events via parallel runs, and (c) live news-feed polling instead
  of manual URL submission — none of which require re-architecting the
  pipeline, only scaling its inputs and the route graph dataset.

---

## 12. Open Questions / Assumptions

- Assuming a single mocked vessel/schedule is sufficient for MVP demo
  impact framing (vs. integrating a real AIS/vessel-schedule feed).
- Assuming the pre-generated route graph for the MVP corridor is built and
  validated manually ahead of the event, not derived live.
- Severity/ranking scoring weights (risk vs. transit time vs. distance) are
  a first-pass heuristic for MVP and should be tunable, not hard-coded
  long-term.
- "Strait of Hormuz" is used as the flagship MVP scenario (correcting what
  appears to be a typo — "strait of hamas" — in the original prompt); this
  also aligns with the crisis-scenario categories already present in the
  reference UI mockup.
