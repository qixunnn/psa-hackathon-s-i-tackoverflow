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
cp .env.example .env
uvicorn app.main:app --reload
```

Set `SUPABASE_URL` and the server-only `SUPABASE_SERVICE_ROLE_KEY` in
`backend/.env` before starting the API. Never expose the service-role key to the
frontend.

To create and seed the current database slice, run these files in the Supabase
SQL Editor in order:

1. `backend/supabase/migrations/001_create_events.sql`
2. `backend/supabase/migrations/002_create_articles_developments_and_replay.sql`
3. `backend/supabase/seed.sql`

The seed resets the four demo replays and creates or refreshes synthetic event
`EVT-001`.

With the backend running, inspect and replay the deterministic demo sequence:

```bash
curl http://localhost:8000/api/v1/demo/articles
curl -X POST http://localhost:8000/api/v1/demo/replay/red-sea-01
curl http://localhost:8000/api/v1/events/EVT-001/developments
```

Replay `red-sea-01` a second time to verify the documented `409 Conflict`
response. Continue with `red-sea-02`, `red-sea-03`, and `red-sea-04` to apply
the complete synthetic confidence progression.

The API is available at `http://127.0.0.1:8000`. Run the backend tests from
the `backend` directory with:

```bash
pytest
```

## Run the Frontend Locally

In a second terminal, from the repository root:

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. The local frontend expects the FastAPI backend at
`http://localhost:8000`; change `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if the
backend is running elsewhere.

Run frontend checks from the `frontend` directory:

```bash
npm run lint
npm run build
```
