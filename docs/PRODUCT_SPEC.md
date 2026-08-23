# Product Specification

**Project Name:** PSA Global Watch

**Version:** 1.0

---

# 1. Vision

PSA Global Watch is an AI-powered Global Maritime Risk Intelligence platform that continuously monitors external maritime and geopolitical disruptions, transforms them into structured operational intelligence, and helps PSA understand what to monitor and how to prepare.

Rather than replacing human decision-making, the platform serves as a decision-support system that provides timely, transparent and explainable risk assessments.

---

# 2. Problem Statement

Global shipping is increasingly affected by events outside the port itself.

Examples include:

- Armed conflicts
- Chokepoint disruptions
- Port strikes
- Severe weather
- Trade restrictions
- Carrier rerouting

Although these events occur globally, they can eventually influence vessel schedules, route choices and operational planning at major transshipment hubs such as PSA.

Today, operators must manually gather information from multiple sources, determine whether an event is relevant, understand how it evolves over time and decide what actions should be considered.

This process is slow, fragmented and difficult to perform consistently.

---

# 3. Product Goal

Transform external disruptions into operational intelligence.

Instead of answering:

> "What happened?"

The platform answers:

- Why is this event relevant?
- Which maritime routes are affected?
- How has the event evolved?
- What assumptions are used?
- What should operators monitor?
- What should operators prepare for?

---

# 4. Target Users

## Primary User

Operations planners and decision makers at PSA.

## Secondary Users

- Port operations managers
- Risk management teams
- Planning teams
- Hackathon judges (demo audience)

---

# 5. User Journey

The intended user experience is:

```
External disruption
        │
        ▼
Global Watch detects event
        │
        ▼
Structured Event Intelligence
        │
        ▼
Route Exposure Analysis
        │
        ▼
Scenario Analysis
        │
        ▼
Potential PSA Impact
        │
        ▼
Monitor / Prepare Recommendations
```

The platform should minimise the amount of manual interpretation required by operators.

---

# 6. Core Features

## 6.1 Maritime Event Detection

The system continuously ingests maritime-relevant news or replayed demo events.

Responsibilities:

- detect relevant events
- reject irrelevant news
- classify disruption type

Output:

A structured event candidate.

---

## 6.2 Event Intelligence

The system transforms raw news into a persistent Event.

Each Event contains:

- title
- location
- event type
- severity
- confidence
- evidence
- affected routes
- affected chokepoints

Multiple articles relating to the same disruption update the existing Event rather than creating duplicates.

---

## 6.3 Event Evolution

Each Event maintains a chronological timeline.

Example:

```
20 Aug
Incident reported

↓

21 Aug
Independent confirmation

↓

22 Aug
Carrier rerouting announced

↓

23 Aug
Second carrier reroutes
```

The system updates:

- confidence
- severity
- evidence
- recommendations

instead of treating each article independently.

---

## 6.4 Route Exposure

For every Event the system identifies:

- affected maritime chokepoints
- affected trade corridors
- possible downstream exposure

The objective is to explain why the disruption matters.

---

## 6.5 Scenario Analysis

The platform performs deterministic scenario modelling using predefined templates.

Examples:

- Carrier rerouting
- Chokepoint disruption
- Canal closure
- Port strike
- Severe weather

Scenario outputs include:

- assumptions
- simulation results
- uncertainty
- operational interpretation

Scenario outputs are decision-support estimates rather than predictions.

---

## 6.6 Operational Impact

The platform translates scenario results into operational language.

Rather than predicting exact operational outcomes, the platform explains possible downstream implications.

Examples:

- Increased arrival uncertainty
- Possible transshipment disruption
- Increased operational monitoring priority

---

## 6.7 Recommendations

Recommendations are divided into two categories.

### Monitor

Signals operators should continue observing.

Examples:

- ETA changes
- Carrier advisories
- Route announcements
- Vessel schedules

### Prepare

Potential planning actions.

Examples:

- Review contingency planning
- Review resource assumptions
- Review yard capacity assumptions

The platform does not autonomously execute operational actions.

---

## 6.8 Activity Log

Every important system action is recorded.

Example:

```
Article received

↓

Maritime relevance identified

↓

Existing event updated

↓

Confidence increased

↓

Scenario re-executed

↓

Recommendations refreshed
```

The Activity Log provides transparency into how the platform reached its conclusions.

---

# 7. MVP Scope

The MVP MUST include:

- Maritime event ingestion (live or replay)
- Maritime relevance classification
- Structured event extraction
- Persistent Event model
- Event Evolution
- Evidence tracking
- Route exposure
- Scenario Analysis
- Operational Impact
- Monitor recommendations
- Prepare recommendations
- Global dashboard
- Activity Log

---

# 8. SHOULD Have

If time permits:

- Synthetic terminal scenario
- Human approval workflow
- Interactive world map
- Scenario parameter adjustments

---

# 9. Stretch Goals

Only after the MVP is complete.

Examples:

- Digital twin
- Autonomous terminal planning
- Live AIS integration
- Multiple simultaneous scenarios
- Multi-agent coordination

---

# 10. Non-Goals

The platform is NOT intended to:

- predict wars
- predict geopolitical events
- replace human operators
- guarantee operational outcomes
- autonomously manage port operations
- replace existing PSA planning systems

---

# 11. Success Criteria

The MVP is considered successful when it can demonstrate the following end-to-end workflow:

1. A new maritime disruption is received.
2. The system determines whether it is relevant.
3. The disruption is transformed into a structured Event.
4. Existing Events are updated if appropriate.
5. Route exposure is identified.
6. A scenario is executed.
7. Potential operational implications are generated.
8. Monitor and Prepare recommendations are produced.
9. The dashboard updates.
10. The Activity Log records every major step.

---

# 12. Design Principles

The project follows these principles.

### Explainable

Users should understand how conclusions were reached.

---

### Transparent

Evidence and assumptions should always be visible.

---

### Human-Centred

Humans remain responsible for operational decisions.

---

### Deterministic

The LLM interprets.

Deterministic application logic performs calculations, validation and policy enforcement.

---

### Hackathon First

The MVP should be demonstrable within the hackathon timeline.

Complex features are deferred until after the MVP is complete.
