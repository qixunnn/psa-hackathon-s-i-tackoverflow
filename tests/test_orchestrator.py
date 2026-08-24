import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.agents import agent1_relevance, agent2_risk, agent3_route_retrieval
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

    def canned_agent2(event):
        return {
            "run_id": event["run_id"],
            "severity": "High",
            "confidence": 0.88,
            "probability": 0.7,
            "affected_chokepoints": ["Strait of Hormuz"],
            "estimated_duration": "3-5 days",
            "rationale": "The disruption affects a major shipping chokepoint.",
            "evidence": [event["evidence"][0]],
        }

    monkeypatch.setattr(agent1_relevance, "run", canned_agent1)
    monkeypatch.setattr(agent2_risk, "run", canned_agent2)
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
    assert "risk_assessment" not in state
    assert "candidate_routes" not in state
    assert "ranked_routes" not in state


def test_successful_agent2_transitions_to_retrieving_routes(client, monkeypatch):
    observed_statuses = []
    original_agent3 = state_machine.agent3_route_retrieval.run

    def observing_agent3(state):
        observed_statuses.append(state["status"])
        return original_agent3(state)

    monkeypatch.setattr(state_machine.agent3_route_retrieval, "run", observing_agent3)
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "complete"
    assert observed_statuses == ["retrieving_routes"]


def test_agent3_attaches_validated_candidates_before_ranking(client, monkeypatch):
    observed_states = []
    original_agent4 = state_machine.agent4_ranking.run

    def observing_agent4(state):
        validate("run", state)
        observed_states.append(
            {
                "status": state["status"],
                "candidate_routes": list(state["candidate_routes"]),
            }
        )
        return original_agent4(state)

    monkeypatch.setattr(state_machine.agent4_ranking, "run", observing_agent4)
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    state = wait_for_run(client, response.json()["run_id"])

    assert state["status"] == "complete"
    assert observed_states[0]["status"] == "ranking"
    assert observed_states[0]["candidate_routes"]


def test_agent3_failure_sets_error_and_does_not_rank(client, monkeypatch):
    def invalid_agent3_input(_state):
        raise agent3_route_retrieval.Agent3Error("Unrecognized chokepoint: Unknown Strait")

    monkeypatch.setattr(agent3_route_retrieval, "run", invalid_agent3_input)
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]
    state = wait_for_run(client, run_id)

    assert state["status"] == "error"
    assert "candidate_routes" not in state
    assert "ranked_routes" not in state
    events = json.loads((main.EVENTS_DIRECTORY / f"{run_id}.json").read_text(encoding="utf-8"))
    assert events[-1]["agent"] == "agent_3_route_retrieval"


def test_unsupported_valid_chokepoint_is_recorded_in_agent3_event(client, monkeypatch):
    def mixed_coverage_risk(event):
        risk = {
            "run_id": event["run_id"],
            "severity": "High",
            "confidence": 0.88,
            "probability": 0.7,
            "affected_chokepoints": ["Bab el-Mandeb", "Strait of Hormuz"],
            "estimated_duration": "3-5 days",
            "rationale": "Two recognized chokepoints may be affected.",
            "evidence": [event["evidence"][0]],
        }
        return risk

    monkeypatch.setattr(agent2_risk, "run", mixed_coverage_risk)
    response = client.post("/runs", json={"source_url": "https://example.com/hormuz"})
    run_id = response.json()["run_id"]
    state = wait_for_run(client, run_id)
    events = json.loads((main.EVENTS_DIRECTORY / f"{run_id}.json").read_text(encoding="utf-8"))

    assert state["status"] == "complete"
    assert [item["route_id"] for item in state["candidate_routes"]] == [
        "RT-001-BASELINE",
        "RT-002-FUJAIRAH-BYPASS",
    ]
    agent3_event = next(item for item in events if item["agent"] == "agent_3_route_retrieval")
    assert "unsupported by the MVP graph: Bab el-Mandeb" in agent3_event["message"]


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
