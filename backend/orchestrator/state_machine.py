"""Synchronous, schema-validated PSA Sentinel pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path

from backend.agents import (
    agent1_relevance,
    agent2_risk,
    agent3_route_retrieval,
    agent4_ranking,
    agent5_advisory,
)
from backend.orchestrator.schema_validation import ValidationError, validate


STORAGE_DIRECTORY = Path(__file__).resolve().parents[1] / "storage"
RUNS_DIRECTORY = STORAGE_DIRECTORY / "runs"
EVENTS_DIRECTORY = STORAGE_DIRECTORY / "events"


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run_path(run_id: str) -> Path:
    return RUNS_DIRECTORY / f"{run_id}.json"


def _events_path(run_id: str) -> Path:
    return EVENTS_DIRECTORY / f"{run_id}.json"


def persist_run(state: dict) -> None:
    RUNS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with _run_path(state["run_id"]).open("w", encoding="utf-8") as run_file:
        json.dump(state, run_file, indent=2)
        run_file.write("\n")


def append_event(run_id: str, agent: str, message: str) -> None:
    EVENTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    path = _events_path(run_id)
    events = []
    if path.exists():
        with path.open(encoding="utf-8") as events_file:
            events = json.load(events_file)
    event = {
        "run_id": run_id,
        "timestamp": _timestamp(),
        "agent": agent,
        "message": message,
    }
    validate("event_log_entry", event)
    events.append(event)
    with path.open("w", encoding="utf-8") as events_file:
        json.dump(events, events_file, indent=2)
        events_file.write("\n")


def _set_status(state: dict, status: str) -> None:
    state["status"] = status
    persist_run(state)


def _validation_failure(state: dict, error: ValidationError) -> None:
    state["status"] = "error"
    persist_run(state)
    append_event(state["run_id"], "orchestrator", f"Schema validation failed: {error}")


def _run_agent(state: dict, status: str, agent_name: str, schema_name: str, agent_callable):
    _set_status(state, status)
    output = agent_callable(state)
    if isinstance(output, list):
        for item in output:
            validate(schema_name, item)
    else:
        validate(schema_name, output)
    return output


def run_pipeline(run_id: str, source_url: str, note: str | None) -> None:
    """Run all stubbed agents synchronously and persist each transition."""
    del note
    state = {
        "run_id": run_id,
        "status": "queued",
        "submitted_by": "operator",
        "submitted_at": _timestamp(),
        "source_url": source_url,
    }
    validate("run", state)
    persist_run(state)

    try:
        event = _run_agent(state, "extracting", "agent_1_relevance", "event", agent1_relevance.run)
        state["event"] = event
        if not event["relevant"]:
            state["status"] = "halted_not_relevant"
            persist_run(state)
            append_event(run_id, "agent_1_relevance", "Article assessed as not relevant; pipeline halted.")
            return
        state["status"] = "assessing_risk"
        persist_run(state)
        append_event(run_id, "agent_1_relevance", "Article extracted and confirmed relevant.")

        risk = _run_agent(state, "assessing_risk", "agent_2_risk", "risk_assessment", agent2_risk.run)
        state["risk_assessment"] = risk
        state["status"] = "retrieving_routes"
        persist_run(state)
        append_event(run_id, "agent_2_risk", "Risk assessment completed.")

        candidates = _run_agent(
            state,
            "retrieving_routes",
            "agent_3_route_retrieval",
            "candidate_route",
            agent3_route_retrieval.run,
        )
        state["candidate_routes"] = candidates
        state["status"] = "ranking"
        persist_run(state)
        append_event(run_id, "agent_3_route_retrieval", "Candidate routes retrieved from route graph.")

        ranked = _run_agent(state, "ranking", "agent_4_ranking", "ranked_route", agent4_ranking.run)
        state["ranked_routes"] = ranked
        state["status"] = "advising"
        persist_run(state)
        append_event(run_id, "agent_4_ranking", "Candidate routes ranked with ETA impact.")

        advisory = _run_agent(state, "advising", "agent_5_advisory", "advisory", agent5_advisory.run)
        state["advisory"] = advisory
        state["status"] = "complete"
        persist_run(state)
        append_event(run_id, "agent_5_advisory", "Advisory generated; operator decision pending.")
    except ValidationError as error:
        _validation_failure(state, error)
