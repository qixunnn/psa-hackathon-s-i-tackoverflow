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
from backend.agents.agent1_relevance import Agent1Error, ArticleExtractionError
from backend.agents.agent2_risk import Agent2Error
from backend.agents.agent3_route_retrieval import Agent3Error
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


def _agent_failure(state: dict, error: Agent1Error) -> None:
    state["status"] = "error"
    persist_run(state)
    append_event(state["run_id"], "agent_1_relevance", f"Agent 1 failed: {error}")


def _agent2_failure(state: dict, error: Agent2Error) -> None:
    state["status"] = "error"
    persist_run(state)
    append_event(state["run_id"], "agent_2_risk", f"Agent 2 failed: {error}")


def _agent3_failure(state: dict, error: Agent3Error) -> None:
    state["status"] = "error"
    persist_run(state)
    append_event(state["run_id"], "agent_3_route_retrieval", f"Agent 3 failed: {error}")


def _run_agent(state: dict, status: str, agent_name: str, schema_name: str, agent_callable):
    _set_status(state, status)
    output = agent_callable(state)
    if isinstance(output, list):
        for item in output:
            validate(schema_name, item)
    else:
        validate(schema_name, output)
    return output


def run_pipeline(
    run_id: str,
    source_url: str,
    note: str | None,
    article_text: str | None = None,
) -> None:
    """Run the sequential pipeline and persist each transition."""
    del note
    run_path = _run_path(run_id)
    if run_path.is_file():
        with run_path.open(encoding="utf-8") as run_file:
            state = json.load(run_file)
        state["status"] = "queued"
    else:
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
        _set_status(state, "extracting")
        agent_input = dict(state)
        if article_text and article_text.strip():
            agent_input["article_text"] = article_text
        event = agent1_relevance.run(agent_input)
        validate("event", event)
        accumulated_state = {**state, "event": event}
        if not event["relevant"]:
            accumulated_state["status"] = "halted_not_relevant"
            validate("run", accumulated_state)
            state = accumulated_state
            persist_run(state)
            append_event(run_id, "agent_1_relevance", "Article assessed as not relevant; pipeline halted.")
            return
        accumulated_state["status"] = "assessing_risk"
        validate("run", accumulated_state)
        state = accumulated_state
        persist_run(state)
        append_event(run_id, "agent_1_relevance", "Article extracted and confirmed relevant.")

        risk = agent2_risk.run(event)
        validate("risk_assessment", risk)
        accumulated_state = {**state, "risk_assessment": risk}
        validate("run", accumulated_state)
        state = accumulated_state
        persist_run(state)
        _set_status(state, "retrieving_routes")
        append_event(run_id, "agent_2_risk", "Risk assessment completed.")

        candidates = _run_agent(
            state,
            "retrieving_routes",
            "agent_3_route_retrieval",
            "candidate_route",
            agent3_route_retrieval.run,
        )
        _, unsupported_chokepoints = agent3_route_retrieval.graph_coverage(state)
        accumulated_state = {**state, "candidate_routes": candidates, "status": "ranking"}
        validate("run", accumulated_state)
        state = accumulated_state
        persist_run(state)
        route_ids = ", ".join(candidate["route_id"] for candidate in candidates) or "none"
        message = f"Candidate route references retrieved from route graph: {route_ids}."
        if unsupported_chokepoints:
            message += (
                " Valid chokepoint(s) unsupported by the MVP graph: "
                + ", ".join(unsupported_chokepoints)
                + "."
            )
        append_event(run_id, "agent_3_route_retrieval", message)

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
    except ArticleExtractionError as error:
        state["status"] = "awaiting_manual_text"
        persist_run(state)
        append_event(run_id, "agent_1_relevance", f"Article text required: {error}")
    except ValidationError as error:
        _validation_failure(state, error)
    except Agent1Error as error:
        _agent_failure(state, error)
    except Agent2Error as error:
        _agent2_failure(state, error)
    except Agent3Error as error:
        _agent3_failure(state, error)
