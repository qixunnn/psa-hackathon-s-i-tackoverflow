# TEAM_CONVENTIONS.md

**Project:** PSA Global Watch
**Version:** 1.0

---

# 1. Purpose

This document defines how the team collaborates during the hackathon.

The goal is to allow four developers to work in parallel without constantly blocking one another or introducing conflicting designs.

If there is ever a disagreement between implementation and documentation:

> **Documentation wins.**

Update the documentation first before changing the implementation.

---

# 2. Team Roles

## Member 1 — Global Watch / AI

Responsible for:

- Article ingestion
- Maritime relevance
- Structured extraction
- Event matching
- Evidence extraction
- Confidence inputs
- Prompt engineering

Owns:

```
/backend/ai
/prompts
```

---

## Member 2 — Backend / Data

Responsible for:

- FastAPI
- Database
- API
- Event persistence
- Activity Log
- Authentication (if required)

Owns:

```
/backend/api
/backend/db
/backend/models
```

---

## Member 3 — Scenario / Risk

Responsible for:

- Maritime knowledge
- Chokepoints
- Route exposure
- Scenario engine
- Monte Carlo
- Operational impact
- Monitor / Prepare

Owns:

```
/backend/scenario
/backend/risk
```

---

## Member 4 — Frontend

Responsible for:

- Dashboard
- Event Detail
- Timeline
- Scenario Lab
- Activity Log
- UX

Owns:

```
/frontend
```

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
 ├── feature/scenario-engine
 └── feature/ai-pipeline
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

Always validate before saving.

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

FastAPI

↓

OpenAI
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

Scenario

- Deterministic outputs
- Assumptions displayed
- Disclaimer shown

---

# 18. Codex Usage

Before asking Codex to write code:

Provide context.

Good prompt:

```
Implement POST /api/v1/events

Follow DATA_SPEC.md

Follow API_SPEC.md

Use FastAPI

Do not invent fields.

Return mock data only.
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

Event Created

↓

Event Timeline Updates

↓

Route Exposure Displayed

↓

Scenario Runs

↓

Operational Impact Generated

↓

Monitor / Prepare Recommendations

↓

Dashboard Updates

↓

Activity Log Updated
```

Everything else is a bonus.

---

# 22. Team Motto

When making technical decisions, ask:

> **Does this improve the demo?**

If the answer is no,

don't build it.