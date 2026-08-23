# TEAM_CONVENTIONS.md

**Project:** PSA Global Watch
**Version:** 1.1

---

# 1. Purpose

This document defines how the team collaborates during the hackathon.

The goal is to allow four developers to work in parallel without constantly blocking one another or introducing conflicting designs.

If there is ever a disagreement between implementation and documentation:

> **Documentation wins.**

Update the documentation first before changing the implementation.

---

# 2. Team Roles

## Member 1 — Global Watch Agent / AI

Responsible for:

- Article ingestion and normalization support
- Maritime relevance classification
- Structured event extraction
- Evidence extraction
- Event-match suggestions
- Confidence input signals
- Global Watch Agent prompts and structured outputs

Owns:

```
/backend/ai/global_watch
/prompts/global_watch
```

Member 1 owns the **Global Watch Agent**, but does not independently change shared Event schemas, final confidence rules, or API contracts.

---

## Member 2 — Backend / Data / Orchestration

Responsible for:

- FastAPI
- Database and Supabase integration
- API implementation
- Event persistence and Event Evolution
- Deterministic event matching thresholds
- Deterministic confidence and severity rules
- Three-agent workflow orchestration
- Activity Log persistence
- Authentication only if required by the MVP

Owns:

```
/backend/api
/backend/db
/backend/models
/backend/services
```

Member 2 owns the deterministic application flow connecting the agents. Agent handoffs must use validated shared models rather than free-form text.

---

## Member 3 — Scenario & Risk + Advisory AI

Responsible for:

- Maritime Knowledge Layer
- Chokepoints and trade corridors
- Route Exposure
- Scenario & Risk Agent
- Predefined deterministic scenario engine
- Monte Carlo where appropriate
- Scenario assumptions and provenance
- Scenario result interpretation
- Advisory Agent
- Operational Impact
- Monitor / Prepare recommendations

Owns:

```
/backend/ai/scenario_risk
/backend/ai/advisory
/backend/scenario
/backend/risk
/prompts/scenario_risk
/prompts/advisory
```

Member 3 owns both downstream AI agents for the MVP. The agents may select, interpret and explain, but deterministic scenario code performs calculations.

---

## Member 4 — Frontend

Responsible for:

- Global Risk Overview
- Event Detail
- Event Evolution timeline
- Evidence and source presentation
- Route Exposure presentation
- Scenario Lab
- Operational Impact
- Monitor / Prepare presentation
- Activity Log
- Agent-handoff visualisation
- UX

Owns:

```
/frontend
```

The frontend must consume backend APIs and must not recreate agent or scenario business logic client-side.

---

# 3. Shared Ownership

The following files belong to everyone.

```
PRODUCT_SPEC.md
ARCHITECTURE.md
DATA_SPEC.md
API_SPEC.md
TEAM_CONVENTIONS.md
```

Do not modify these casually.

Major changes require team agreement.

---

# 4. Git Workflow

Never push directly to main.

Workflow:

```
main
 │
 ├── feature/frontend-dashboard
 ├── feature/event-engine
 ├── feature/global-watch-agent
 ├── feature/scenario-risk-agent
 └── feature/advisory-agent
```

Each feature should be completed through a Pull Request.

---

# 5. Branch Naming

Use:

```
feature/<feature>

bugfix/<issue>

docs/<topic>

refactor/<area>
```

Examples

```
feature/event-memory

feature/scenario-engine

bugfix/api-validation

docs/data-spec
```

---

# 6. Commit Convention

Good commits explain intent.

Examples

```
feat: add event persistence

feat: implement replay endpoint

fix: prevent duplicate events

docs: update API contract

refactor: simplify scenario engine
```

Avoid:

```
update

fix stuff

changes

asdf
```

---

# 7. Pull Requests

A PR should answer:

- What changed?
- Why?
- Screenshots (if UI)
- Breaking changes?
- Documentation updated?

Small PRs are preferred.

---

# 8. Definition of Done

A feature is complete only if:

✅ Works

✅ Code reviewed

✅ Documentation updated

✅ No TypeScript/Python errors

✅ No console errors

✅ No hardcoded secrets

For AI-agent features:

✅ Output follows the structured schema in `DATA_SPEC.md`

✅ Output is validated before persistence or downstream use

✅ Major agent actions create Activity Log entries

For scenario features:

✅ Calculations remain deterministic

✅ Assumptions and provenance are visible

✅ Scenario language does not present simulations as guaranteed predictions

---

# 9. Documentation First

Before implementing:

```
Need new field?
        │
        ▼
Update DATA_SPEC.md
        │
        ▼
Update API_SPEC.md
        │
        ▼
Implement
```

Never invent API responses while coding.

---

# 10. Single Source of Truth

| Concern | Source |
|----------|--------|
| Product | PRODUCT_SPEC.md |
| Architecture | ARCHITECTURE.md |
| Data Models | DATA_SPEC.md |
| API | API_SPEC.md |
| Team Workflow | TEAM_CONVENTIONS.md |

If two files disagree, resolve the inconsistency immediately.

---

# 11. Coding Standards

## Backend

- Python
- Type hints
- Pydantic models
- Small functions
- No business logic inside routes

---

## Frontend

- TypeScript only
- Functional React components
- Reusable UI components
- No duplicated API logic

---

## AI

Prompt outputs must be structured.

Never trust raw LLM text.

Always validate before saving or passing output to another agent.

The three MVP agents are:

```text
GLOBAL_WATCH
SCENARIO_RISK
ADVISORY
```

Agents communicate through validated domain objects and persistent Event state.

Do not pass hidden chain-of-thought between agents.

The LLM may interpret, select and explain.

Deterministic code must perform validation, calculations, confidence/severity rules and policy enforcement.

---

# 12. Environment Variables

Never commit:

```
.env
.env.local
```

Use:

```
.env.example
```

Example

```
OPENAI_API_KEY=

SUPABASE_URL=

SUPABASE_ANON_KEY=
```

---

# 13. Secrets

Never commit:

- API keys
- Tokens
- Service role keys
- Passwords

Use environment variables.

---

# 14. Mock Data

Until backend APIs exist:

Frontend should use

```
/mock
```

Example

```
mock/events.ts

mock/scenario.ts

mock/activity.ts
```

This allows frontend work to continue independently.

---

# 15. API Rule

Frontend never talks directly to OpenAI.

Flow:

```
Frontend
   ↓
FastAPI / Workflow Orchestrator
   ├── Global Watch Agent
   ├── Scenario & Risk Agent
   └── Advisory Agent
            ↓
Deterministic services / database
```

All AI calls stay server-side.

---

# 16. Scope Discipline

If a feature is not in PRODUCT_SPEC.md:

Do not build it.

Avoid:

- extra dashboards
- unnecessary authentication
- microservices
- Kubernetes
- Redis
- Kafka
- complex DevOps

Keep the MVP focused.

---

# 17. Testing

Minimum checks before merging:

Backend

- Endpoint works
- Schema validates
- No crashes

Frontend

- Responsive layout
- No console errors
- Handles loading state
- Handles error state

AI Agents

- Structured output validates
- Invalid output fails safely
- Agent handoff uses shared domain models
- Activity Log identifies the responsible agent
- No hidden chain-of-thought is exposed

Scenario

- Deterministic outputs
- Assumptions and provenance displayed
- Disclaimer shown
- LLM does not invent mathematical models

---

# 18. Codex Usage

Before asking Codex to write code:

Provide context.

Good prompt:

```
Implement the Global Watch article-processing vertical slice.

Read first:
- PRODUCT_SPEC.md
- ARCHITECTURE.md
- DATA_SPEC.md
- API_SPEC.md
- TEAM_CONVENTIONS.md

Implement only:
POST /api/v1/articles/process

Follow DATA_SPEC.md and API_SPEC.md exactly.

Use FastAPI and Pydantic.

The Global Watch Agent must return structured output.

Validate AI output before persistence.

Do not let the LLM set final confidence or severity.

Record major processing stages in the Activity Log.

Do not invent fields or add unrelated features.
```

Avoid vague prompts like:

```
Build the backend.
```

---

# 19. Daily Sync

At the start of each work session:

Each member answers:

- What did I finish?
- What am I doing?
- Am I blocked?

Keep updates under five minutes.

---

# 20. Demo Freeze

24 hours before presentation:

No new features.

Only:

- bug fixes
- UI polish
- documentation
- demo rehearsal

---

# 21. MVP Success Checklist

The project is demo-ready when the following flow works end-to-end:

```
Replay Article
      ↓
Global Watch Agent
      ↓
Event Created / Updated
      ↓
Evidence + Event Evolution Updated
      ↓
Scenario & Risk Agent
      ↓
Route Exposure Resolved
      ↓
Predefined Scenario Selected
      ↓
Deterministic Scenario Engine Runs
      ↓
Scenario & Risk Agent Interprets Results
      ↓
Advisory Agent
      ↓
Operational Impact Generated
      ↓
Monitor / Prepare Recommendations
      ↓
Dashboard Updates
      ↓
Activity Log Shows Agent Handoffs
```

The Activity Log should make this sequence visible:

```text
GLOBAL_WATCH → SCENARIO_RISK → ADVISORY
```

The three-agent workflow is part of the MVP, not a stretch goal.

Everything else is a bonus.

---

# 22. Team Motto

When making technical decisions, ask:

> **Does this improve the demo?**

If the answer is no,

don't build it.