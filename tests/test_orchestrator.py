import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.agents import agent2_risk
from backend.orchestrator import state_machine
from backend.orchestrator.schema_validation import validate


@pytest.fixture
def client(tmp_path, monkeypatch):
    runs_directory = tmp_path / "runs"
    events_directory = tmp_path / "events"
    monkeypatch.setattr(state_machine, "RUNS_DIRECTORY", runs_directory)
    monkeypatch.setattr(state_machine, "EVENTS_DIRECTORY", events_directory)
    monkeypatch.setattr(main, "RUNS_DIRECTORY", runs_directory)
    monkeypatch.setattr(main, "EVENTS_DIRECTORY", events_directory)
    return TestClient(main.app)


def wait_for_run(client, run_id):
    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    return response.json()


def test_normal_run_completes_with_all_outputs(client):
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    assert response.status_code == 202
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "complete"
    for entity_name, key in [
        ("event", "event"),
        ("risk_assessment", "risk_assessment"),
        ("candidate_route", "candidate_routes"),
        ("ranked_route", "ranked_routes"),
        ("advisory", "advisory"),
    ]:
        value = state[key]
        values = value if isinstance(value, list) else [value]
        for payload in values:
            validate(entity_name, payload)


def test_irrelevant_run_halts_without_downstream_outputs(client):
    response = client.post("/runs", json={"source_url": "https://example.com/irrelevant"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "halted_not_relevant"
    assert "risk_assessment" not in state
    assert "candidate_routes" not in state
    assert "ranked_routes" not in state
    assert "advisory" not in state


def test_invalid_risk_output_stops_pipeline(client, monkeypatch):
    def invalid_risk(_state):
        return {"severity": "High"}

    monkeypatch.setattr(agent2_risk, "run", invalid_risk)
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "error"
    assert "candidate_routes" not in state
    assert "ranked_routes" not in state


def test_run_and_event_files_are_valid_json(client):
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]
    run_path = main.RUNS_DIRECTORY / f"{run_id}.json"
    events_path = main.EVENTS_DIRECTORY / f"{run_id}.json"

    assert run_path.is_file()
    assert events_path.is_file()
    json.loads(run_path.read_text(encoding="utf-8"))
    json.loads(events_path.read_text(encoding="utf-8"))


def test_events_endpoint_returns_run_events(client):
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]

    events_response = client.get(f"/runs/{run_id}/events")

    assert events_response.status_code == 200
    assert len(events_response.json()) == 5


def test_routes_endpoint_returns_route_graph(client):
    response = client.get("/routes")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert {route["route_id"] for route in response.json()} == {
        "RT-001-BASELINE",
        "RT-002-FUJAIRAH-BYPASS",
        "RT-003-ESCORTED-TRANSIT",
    }


def test_decision_updates_and_persists_advisory(client):
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]

    decision = client.post(
        f"/runs/{run_id}/decision",
        json={"decision": "accepted", "comment": "Proceed with berth planning."},
    )
    assert decision.status_code == 200
    state = wait_for_run(client, run_id)

    assert state["advisory"]["operator_decision"] == "accepted"
    assert state["advisory"]["operator_comment"] == "Proceed with berth planning."


def test_complete_event_log_has_five_ordered_agent_entries(client):
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]
    events = json.loads((main.EVENTS_DIRECTORY / f"{run_id}.json").read_text(encoding="utf-8"))

    assert len(events) == 5
    assert [event["agent"] for event in events] == [
        "agent_1_relevance",
        "agent_2_risk",
        "agent_3_route_retrieval",
        "agent_4_ranking",
        "agent_5_advisory",
    ]
    assert all(event["timestamp"] and event["message"] for event in events)
