# PSA Global Watch

> An AI-powered Global Maritime Risk Intelligence platform that transforms global maritime and geopolitical disruptions into actionable operational intelligence for PSA.

---

## Overview

Global supply chains are increasingly affected by geopolitical conflicts, port strikes, severe weather, trade restrictions and disruptions at key maritime chokepoints.

While these events occur outside Singapore, they can eventually influence vessel schedules, route choices and operational planning for major transshipment hubs such as PSA.

PSA Global Watch continuously monitors external maritime events, analyses their operational relevance, and provides decision-support recommendations that help operators understand what to monitor and how to prepare.

This project is built for the PSA Hackathon.

---

# Problem Statement

Current information about global disruptions is fragmented across news outlets, maritime bulletins and public reports.

Operators must manually determine:

- Which events are relevant.
- Which shipping routes are affected.
- Whether PSA should be concerned.
- What operational actions should be considered.

This process is time-consuming and difficult to perform consistently.

---

# Our Solution

PSA Global Watch converts external disruptions into operational intelligence.

Instead of simply summarising news, the platform:

1. Detects maritime-relevant events.
2. Tracks each disruption as an evolving event.
3. Maps affected chokepoints and shipping routes.
4. Evaluates possible downstream operational impacts.
5. Generates Monitor and Prepare recommendations.
6. Provides transparent reasoning, evidence and confidence.

---

# Core Workflow

```text
External Event
      │
      ▼
Maritime Relevance
      │
      ▼
Event Intelligence
      │
      ▼
Route Exposure
      │
      ▼
Scenario Analysis
      │
      ▼
Potential PSA Impact
      │
      ▼
Monitor / Prepare
```

---

# MVP Scope

The MVP focuses on the following capabilities:

- Maritime news ingestion
- Structured event extraction
- Persistent event memory
- Evidence and source tracking
- Chokepoint and route mapping
- Scenario analysis
- Potential PSA impact assessment
- Monitor / Prepare recommendations
- Global risk dashboard
- Activity log

---

# Technology Stack

Frontend

- Next.js
- TypeScript
- Tailwind CSS

Backend

- FastAPI
- Python
- Pydantic

Database

- Supabase PostgreSQL

AI

- OpenAI API

Simulation

- NumPy

Maps

- MapLibre / Mapbox

---

# Architecture Principles

The project follows one important design principle:

> **LLM interprets. Deterministic code calculates.**

The LLM is responsible for understanding and structuring information.

Deterministic application logic is responsible for calculations, validation, persistence, authorization and scenario execution.

---

# Repository Structure

```
docs/
frontend/
backend/
data/
```

Documentation is written before implementation to support collaborative development.

---

# Team

This project is developed by Team Sitack Overflow for the PSA Hackathon.

---

# Run the Backend Locally

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Run the backend tests from
the `backend` directory with:

```bash
pytest
```
