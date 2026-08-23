# Product Specification

**Project Name:** PSA Global Watch  
**Version:** 1.1

---

# 1. Vision

PSA Global Watch is a **three-agent Global Maritime Risk Intelligence platform** that continuously monitors external maritime and geopolitical disruptions, maintains an evolving understanding of those events, analyses potential downstream maritime risks, and provides actionable decision support for PSA.

The platform uses three cooperating AI agents:

1. **Global Watch Agent** — observes and interprets maritime disruptions.
2. **Scenario & Risk Agent** — analyses route exposure and selects appropriate analytical tools.
3. **Advisory Agent** — translates validated findings into operational implications and Monitor / Prepare recommendations.

Rather than replacing human decision-making, PSA Global Watch supports planners with timely, transparent and explainable intelligence.

---

# 2. Problem Statement

Global shipping is increasingly affected by events occurring far outside the port itself.

Examples include:

- armed conflicts
- chokepoint disruptions
- port strikes
- severe weather
- trade restrictions
- sanctions
- piracy and security incidents
- carrier rerouting

Although these disruptions occur globally, they may eventually influence vessel schedules, shipping routes, transshipment connections and operational planning at major maritime hubs such as Singapore.

Relevant information is distributed across news reports, carrier advisories, maritime bulletins and authority notices.

Operators must manually determine:

- which developments are maritime-relevant
- whether multiple reports relate to the same disruption
- how an event is evolving
- which routes or chokepoints may be affected
- what downstream implications should be investigated
- what signals should be monitored
- what contingency preparations should be considered

This process is fragmented, time-consuming and difficult to perform consistently.

---

# 3. Product Goal

The goal of PSA Global Watch is to:

> **Transform continuously evolving global maritime disruptions into structured, explainable and actionable operational intelligence.**

Instead of only answering:

> "What happened?"

the platform should help answer:

- Why does this event matter?
- Is this new information or part of an existing disruption?
- How has the disruption evolved?
- Which maritime routes or chokepoints may be affected?
- What evidence supports the current assessment?
- What assumptions are being made?
- What possible downstream scenarios should be analysed?
- What should PSA monitor?
- What should PSA consider preparing for?

---

# 4. Target Users

## Primary Users

PSA operations planners and decision makers.

## Secondary Users

- port operations managers
- risk management teams
- planning teams
- resilience and business-continuity teams

For the hackathon, judges are the primary demonstration audience, but the product should be designed around a realistic operational-planning user.

---

# 5. Agentic AI Architecture

PSA Global Watch uses three AI agents with clearly separated responsibilities.

```text
External Maritime Information
            │
            ▼
┌────────────────────────────┐
│     Global Watch Agent     │
│                            │
│ Observe                    │
│ Interpret                  │
│ Verify                     │
└─────────────┬──────────────┘
              │
              ▼
      Persistent Event Memory
              │
              ▼
┌────────────────────────────┐
│   Scenario & Risk Agent    │
│                            │
│ Analyse route exposure     │
│ Select analytical tool     │
│ Prepare model inputs       │
│ Interpret model outputs    │
└─────────────┬──────────────┘
              │
              ▼
     Deterministic Scenario
            Engine
              │
              ▼
┌────────────────────────────┐
│       Advisory Agent       │
│                            │
│ Operational implications   │
│ Monitor recommendations    │
│ Prepare recommendations    │
└─────────────┬──────────────┘
              │
              ▼
          Dashboard
```

The agents communicate through validated structured data and persistent Event state.

They do not rely on hidden conversational memory.

---

# 6. Agent Responsibilities

## 6.1 Global Watch Agent

The Global Watch Agent is responsible for understanding incoming external information and maintaining an evolving representation of maritime disruptions.

Responsibilities include:

- determine maritime relevance
- classify disruption type
- extract structured facts
- extract supporting evidence
- identify relevant locations
- suggest affected chokepoints
- compare new information with existing Events
- suggest whether an Event should be created or updated
- contribute evidence used by deterministic confidence logic

The Global Watch Agent does **not** directly assign final severity or confidence without deterministic validation.

### Output

Structured intelligence that can create or update a persistent Event.

---

## 6.2 Scenario & Risk Agent

The Scenario & Risk Agent determines how a validated Event should be analysed.

Responsibilities include:

- interpret Event context
- resolve relevant maritime routes and chokepoints
- consult the Maritime Knowledge Layer
- select an appropriate predefined scenario model
- identify or extract scenario parameters
- provide validated inputs to the deterministic Scenario Engine
- interpret Scenario Engine results
- produce a structured risk assessment

The Scenario & Risk Agent does **not** invent mathematical models or simulation results.

### Output

A validated scenario selection, model inputs and interpretation of deterministic outputs.

---

## 6.3 Advisory Agent

The Advisory Agent converts validated Event and scenario information into operator-facing decision support.

Responsibilities include:

- explain potential PSA relevance
- summarise possible operational implications
- generate Monitor recommendations
- generate Prepare recommendations
- explain why recommendations follow from available evidence and scenario outputs

The Advisory Agent does not autonomously execute operational actions.

### Output

Operational Impact plus Monitor / Prepare recommendations.

---

# 7. User Journey

The intended workflow is:

```text
External disruption detected
        │
        ▼
Global Watch Agent
interprets new information
        │
        ▼
Persistent Event created/updated
        │
        ▼
Evidence + Event Evolution updated
        │
        ▼
Scenario & Risk Agent
analyses route exposure
        │
        ▼
Deterministic Scenario Engine
        │
        ▼
Advisory Agent
        │
        ▼
Potential PSA Impact
        │
        ▼
Monitor / Prepare Recommendations
```

When additional information arrives, the process repeats against the same persistent Event where appropriate.

---

# 8. Core Features

## 8.1 Maritime Event Detection

The system ingests maritime information from live sources or controlled replay data.

The Global Watch Agent determines:

- whether the information is maritime-relevant
- what type of disruption may be occurring
- whether further processing should continue

Irrelevant information should be discarded before expensive downstream processing.

---

## 8.2 Persistent Event Intelligence

Raw articles are not treated as independent Events.

Multiple reports may contribute to the same persistent Event.

Each Event contains:

- title
- summary
- event type
- location
- status
- severity
- confidence
- sources
- evidence
- affected routes
- affected chokepoints
- developments
- scenario results
- recommendations

---

## 8.3 Event Evolution

Events evolve when new information becomes available.

Example:

```text
20 Aug
Initial incident reported
Confidence: 0.41

        ↓

21 Aug
Independent source confirms disruption
Confidence: 0.63

        ↓

22 Aug
Carrier announces rerouting
Severity: MEDIUM → HIGH
Confidence: 0.82

        ↓

23 Aug
Additional confirmation received
Confidence: 0.91
```

The system should update the existing Event rather than create duplicate independent alerts.

Event Evolution may update:

- evidence
- confidence
- severity
- status
- route exposure
- scenario results
- operational implications
- recommendations

---

## 8.4 Evidence and Source Tracking

Important claims must remain traceable to their source.

Users should be able to distinguish:

- original source information
- extracted evidence
- AI interpretation
- model assumptions
- calculated outputs

The system must not present unsupported AI-generated statements as observed facts.

---

## 8.5 Route Exposure

The system identifies relevant:

- maritime chokepoints
- trade corridors
- route relationships
- alternative routes

Example:

```text
Bab el-Mandeb disruption
          │
          ▼
Red Sea / Suez route
          │
          ▼
Asia-Europe corridor
          │
          ▼
Possible Cape of Good Hope rerouting
```

The purpose is to explain why an external disruption may matter downstream.

---

## 8.6 Scenario Analysis

The Scenario & Risk Agent selects from predefined scenario models.

Initial scenario types may include:

- Carrier Rerouting
- Chokepoint Disruption
- Canal Closure
- Port Strike
- Severe Weather
- Trade Restriction

The LLM does not invent the underlying mathematical model.

The deterministic Scenario Engine performs calculations.

Scenario results should expose:

- scenario type
- assumptions
- assumption provenance
- model parameters
- numerical outputs
- uncertainty
- interpretation

Scenario results are **decision-support estimates**, not guaranteed predictions.

---

## 8.7 Operational Impact

The Advisory Agent translates validated intelligence and scenario results into potential operational implications.

Examples:

- vessel arrival variability may increase
- schedule reliability may decrease
- transshipment connections could face additional pressure
- monitoring priority may increase

The system must avoid unsupported precision where real PSA operational data is unavailable.

---

## 8.8 Monitor Recommendations

Monitor recommendations identify signals that operators should continue watching.

Examples:

- vessel ETA changes
- carrier advisories
- additional rerouting announcements
- chokepoint status
- schedule reliability
- additional independent confirmation

---

## 8.9 Prepare Recommendations

Prepare recommendations describe potential planning considerations.

Examples:

- review contingency capacity
- review affected transshipment flows
- review operational planning assumptions
- prepare for increased schedule variability

Recommendations remain advisory.

---

## 8.10 Activity Log

The Activity Log makes the agentic workflow visible.

Example:

```text
02:31:02  GLOBAL WATCH   OBSERVE
           Article ingested

02:31:04  GLOBAL WATCH   INTERPRET
           Maritime relevance: HIGH

02:31:06  GLOBAL WATCH   VERIFY
           Matched existing EVT-001

02:31:07  SYSTEM         VERIFY
           Confidence 0.63 → 0.82

02:31:09  SCENARIO_RISK  MODEL
           Asia-Europe route exposure identified

02:31:10  SCENARIO_RISK  MODEL
           Carrier rerouting scenario selected

02:31:11  SYSTEM         MODEL
           Simulation completed

02:31:13  SCENARIO_RISK  ASSESS
           Scenario results interpreted

02:31:15  ADVISORY       RECOMMEND
           Monitor / Prepare advisory generated
```

The Activity Log exposes:

- responsible agent
- stage
- action
- concise result
- timestamps
- success/failure status

It must not expose hidden chain-of-thought.

---

# 9. Deterministic Services

Not every system component is an AI agent.

The following remain deterministic application services:

- Pydantic validation
- duplicate detection
- confidence calculation
- severity rules
- database persistence
- scenario calculations
- Monte Carlo simulation
- authorization and policy rules
- API behaviour

The architectural principle is:

> **Agents interpret, choose and explain. Deterministic services validate, calculate and enforce.**

---

# 10. MVP Scope

The MVP MUST demonstrate the complete three-agent workflow.

Required capabilities:

- maritime event ingestion
- Global Watch Agent
- maritime relevance classification
- structured event extraction
- persistent Event model
- Event matching/update behaviour
- Event Evolution
- evidence tracking
- deterministic confidence handling
- route/chokepoint exposure
- Scenario & Risk Agent
- at least one predefined deterministic scenario model
- scenario assumptions and provenance
- scenario results
- Advisory Agent
- Operational Impact
- Monitor recommendations
- Prepare recommendations
- Global Risk Overview
- Event Detail
- Activity Log showing agent handoffs

The project is not considered complete if only the dashboard or replay mechanism works without the agent workflow.

---

# 11. SHOULD Have

If time permits:

- interactive world map
- adjustable Scenario Lab parameters
- multiple predefined scenario models
- live external information source
- source verification across multiple live feeds
- richer activity visualisation

---

# 12. Stretch Goals

Only after the MVP works end to end:

- live AIS integration
- multiple simultaneous disruptions
- more advanced maritime route modelling
- synthetic downstream terminal scenario
- human approval workflow for simulated actions
- digital twin integration
- autonomous terminal planning research

The three-agent architecture itself is **not** a stretch goal.

It is part of the MVP.

---

# 13. Non-Goals

PSA Global Watch is NOT intended to:

- predict wars
- predict geopolitical events before evidence exists
- guarantee future operational outcomes
- replace PSA operators
- replace PSA planning systems
- autonomously control port equipment
- generate unsupported berth or yard allocations
- fabricate PSA operational data
- allow LLMs to invent mathematical models
- allow LLMs to bypass deterministic safety or validation rules

---

# 14. Synthetic Demo Data

Synthetic data may be used where real operational data is unavailable.

Synthetic content must always be clearly labelled.

Examples include:

- replay articles
- scenario assumptions
- hypothetical vessel patterns
- optional terminal demonstrations

Synthetic demonstration data must never be presented as actual PSA data.

---

# 15. Success Criteria

The MVP is successful when it demonstrates the following end-to-end flow:

1. A new maritime article or bulletin is received.
2. The **Global Watch Agent** determines whether it is relevant.
3. The agent extracts structured facts and evidence.
4. The system determines whether to create or update an Event.
5. Persistent Event memory is updated.
6. Event Evolution records the new development.
7. Route/chokepoint exposure is identified.
8. The **Scenario & Risk Agent** selects an appropriate predefined scenario model.
9. Deterministic scenario calculations execute.
10. The Scenario & Risk Agent interprets the results.
11. The **Advisory Agent** generates potential operational implications.
12. Monitor recommendations are generated.
13. Prepare recommendations are generated.
14. The dashboard updates.
15. The Activity Log clearly shows the handoff between agents.

A successful demo should allow a judge to see:

```text
Observe
   ↓
Interpret
   ↓
Remember
   ↓
Analyse
   ↓
Model
   ↓
Assess
   ↓
Recommend
```

without requiring the user to manually prompt every stage.

---

# 16. Demo Success Story

The preferred demonstration uses one evolving maritime disruption.

Example:

```text
Initial incident
       │
       ▼
Global Watch creates Event
       │
       ▼
New article arrives
       │
       ▼
Global Watch recognises same Event
       │
       ▼
Confidence / severity changes
       │
       ▼
Scenario & Risk Agent reruns analysis
       │
       ▼
Advisory Agent refreshes recommendations
```

The central demo message is:

> **PSA Global Watch does not simply summarise maritime news. Its agents maintain an evolving understanding of global disruptions, analyse potential downstream consequences using validated tools, and continuously refresh decision-support recommendations for PSA.**

---

# 17. Design Principles

## Agentic

The system should autonomously progress through the intelligence workflow when new information arrives.

Human users should not need to manually prompt each agent.

---

## Explainable

Users should understand why an Event was classified, updated or considered operationally relevant.

---

## Evidence-Grounded

Agent outputs should remain connected to evidence, maritime knowledge or deterministic model results.

---

## Transparent

Assumptions, uncertainty and synthetic data must be visible.

---

## Persistent

The system maintains Event state across multiple developments instead of treating every article independently.

---

## Human-Centred

Humans remain responsible for operational decisions.

---

## Deterministic Where Appropriate

LLMs interpret unstructured information.

Deterministic services perform validation, calculations and policy enforcement.

---

## Hackathon First

The complete end-to-end agentic workflow is more important than adding many partially implemented features.

A small system with three working agents is preferable to a large system with numerous disconnected capabilities.