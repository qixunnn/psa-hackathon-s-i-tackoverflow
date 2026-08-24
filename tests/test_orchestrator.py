import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.agents import agent1_relevance, agent2_risk
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

    def canned_agent1(state):
        relevant = "irrelevant" not in state["source_url"]
        return {
            "run_id": state["run_id"],
            "relevant": relevant,
            "confidence": 0.9,
            "relevance_rationale": "The submitted article was assessed against PSA-bound shipping.",
            "summary": "A validated test article.",
            "entities": {
                "location": "Strait of Hormuz" if relevant else "Domestic market",
                "event_type": "geopolitical tension" if relevant else "labor dispute",
                "date": "2026-08-25",
                "actors": ["Shipping operators"] if relevant else ["Domestic workers"],
                "chokepoints_mentioned": ["Strait of Hormuz"] if relevant else [],
            },
            "evidence": ["A concise source-backed test excerpt."],
            "source_url": state["source_url"],
            "extracted_at": "2026-08-25T00:00:00Z",
        }

    monkeypatch.setattr(agent1_relevance, "run", canned_agent1)
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


def test_scraping_failure_is_recoverable_manual_text_state(client, monkeypatch):
    def scraping_failure(_state):
        raise agent1_relevance.ArticleExtractionError("No readable article text")

    monkeypatch.setattr(agent1_relevance, "run", scraping_failure)
    response = client.post("/runs", json={"source_url": "https://example.com/paywall"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "awaiting_manual_text"
    assert state["status"] != "error"
    assert "event" not in state


def test_manual_article_text_resumes_same_run(client, monkeypatch):
    received_text = []

    def resumable_agent(state):
        received_text.append(state.get("article_text"))
        if not state.get("article_text"):
            raise agent1_relevance.ArticleExtractionError("Manual text required")
        return {
            "run_id": state["run_id"],
            "relevant": False,
            "confidence": 0.94,
            "relevance_rationale": "The article has no maritime or PSA-bound shipping impact.",
            "summary": "The article concerns a domestic retail event.",
            "entities": {
                "location": "Singapore",
                "event_type": "retail event",
                "date": "2026-08-25",
                "actors": ["Retailers"],
                "chokepoints_mentioned": [],
            },
            "evidence": ["Retail sales increased during the holiday period."],
            "source_url": state["source_url"],
            "extracted_at": "2026-08-25T00:00:00Z",
        }

    monkeypatch.setattr(agent1_relevance, "run", resumable_agent)
    created = client.post("/runs", json={"source_url": "https://example.com/paywall"})
    run_id = created.json()["run_id"]
    assert wait_for_run(client, run_id)["status"] == "awaiting_manual_text"

    resumed = client.post(
        f"/runs/{run_id}/article-text",
        json={"article_text": "Retail sales increased during the holiday period."},
    )

    assert resumed.status_code == 202
    state = wait_for_run(client, run_id)
    assert state["status"] == "halted_not_relevant"
    assert state["event"]["relevant"] is False
    assert received_text == [None, "Retail sales increased during the holiday period."]


def test_malformed_gemini_output_sets_pipeline_error(client, monkeypatch):
    def malformed_response(_state):
        raise agent1_relevance.GeminiResponseError("Gemini returned malformed JSON")

    monkeypatch.setattr(agent1_relevance, "run", malformed_response)
    response = client.post("/runs", json={"source_url": "https://example.com/malformed"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "error"
    assert "risk_assessment" not in state
