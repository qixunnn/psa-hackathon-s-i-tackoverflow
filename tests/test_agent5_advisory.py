import json
from types import SimpleNamespace

import pytest

from backend.agents import agent5_advisory
from backend.config import GeminiSettings
from backend.orchestrator.schema_validation import ValidationError, validate


SETTINGS = GeminiSettings(api_key="test-key", model="gemini-2.5-flash")


class FakeModels:
    def __init__(self, payload=None, text=None, error=None):
        self.payload = payload
        self.text = text
        self.error = error
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        response_text = self.text if self.text is not None else json.dumps(self.payload)
        return SimpleNamespace(text=response_text)


def fake_client(payload=None, text=None, error=None):
    models = FakeModels(payload=payload, text=text, error=error)
    return SimpleNamespace(models=models), models


def valid_state():
    return {
        "run_id": "run-5",
        "status": "advising",
        "submitted_by": "operator",
        "submitted_at": "2026-08-25T10:00:00Z",
        "source_url": "https://example.com/article",
        "event": {
            "run_id": "run-5",
            "relevant": True,
            "confidence": 0.91,
            "relevance_rationale": "The article affects PSA-bound maritime shipping.",
            "summary": "A carrier suspended transit through the Strait of Hormuz.",
            "entities": {
                "location": "Strait of Hormuz",
                "event_type": "maritime disruption",
                "date": "2026-08-25",
                "actors": ["Carrier"],
                "chokepoints_mentioned": ["Strait of Hormuz"],
            },
            "evidence": ["Transit through the strait was temporarily suspended."],
            "source_url": "https://example.com/article",
            "extracted_at": "2026-08-25T10:01:00Z",
        },
        "risk_assessment": {
            "run_id": "run-5",
            "severity": "High",
            "confidence": 0.87,
            "probability": 0.72,
            "affected_chokepoints": ["Strait of Hormuz"],
            "estimated_duration": "3-5 days",
            "rationale": "The event may materially disrupt transit.",
            "evidence": ["Transit through the strait was temporarily suspended."],
        },
        "candidate_routes": [
            {
                "run_id": "run-5",
                "route_id": "RT-001-BASELINE",
                "retrieved_reason": "Baseline route retained for comparison.",
            }
        ],
        "ranked_routes": [
            {
                "run_id": "run-5",
                "route_id": "RT-002-FUJAIRAH-BYPASS",
                "rank": 1,
                "score": 0.83,
                "eta": "2026-09-06T00:00:00Z",
                "eta_delta_days": 2,
                "rationale": "Avoids Hormuz with a two-day ETA impact.",
            }
        ],
    }


def advisory_payload():
    return {
        "headline": "Prepare for possible Hormuz-driven delay",
        "summary": "A validated Strait of Hormuz disruption may shift the PSA-bound vessel by about two days.",
        "recommended_actions": [
            "Review berth and yard allocation",
            "Notify transshipment partners of the watch status",
        ],
    }


def test_agent5_generates_valid_advisory_from_gemini_fields():
    client, models = fake_client(payload=advisory_payload())

    advisory = agent5_advisory.run(valid_state(), client=client, settings=SETTINGS)

    validate("advisory", advisory)
    assert advisory["run_id"] == "run-5"
    assert advisory["operator_decision"] == "pending"
    assert advisory["operator_comment"] is None
    assert advisory["confidence"] == 0.83
    assert advisory["headline"] == "Prepare for possible Hormuz-driven delay"
    assert models.calls[0]["config"]["response_mime_type"] == "application/json"
    system_instruction = " ".join(models.calls[0]["config"]["system_instruction"].split())
    assert "PSA's operational control" in system_instruction
    assert "alter vessel navigation, routing, vessel speed" in system_instruction
    assert "PSA may identify or monitor a route selected by the shipping line" in system_instruction
    assert "ranked_routes" in models.calls[0]["contents"]


def test_agent5_rejects_invalid_input_before_gemini_call():
    state = valid_state()
    state["ranked_routes"][0].pop("rationale")
    client, models = fake_client(payload=advisory_payload())

    with pytest.raises(ValidationError):
        agent5_advisory.run(state, client=client, settings=SETTINGS)
    assert models.calls == []


def test_agent5_allows_relevant_no_route_exposure_advisory():
    state = valid_state()
    state["risk_assessment"]["severity"] = "Low"
    state["risk_assessment"]["probability"] = 0.3
    state["risk_assessment"]["affected_chokepoints"] = []
    state["candidate_routes"] = []
    state["ranked_routes"] = []
    payload = {
        "headline": "Monitor regulatory transshipment exposure",
        "summary": "The event creates compliance risk but no immediate route exposure for the MVP corridor.",
        "recommended_actions": ["Monitor enforcement guidance", "Review documentation readiness"],
    }
    client, _ = fake_client(payload=payload)

    advisory = agent5_advisory.run(state, client=client, settings=SETTINGS)

    validate("advisory", advisory)
    assert advisory["confidence"] == 0.87
    assert advisory["recommended_actions"] == [
        "Monitor enforcement guidance",
        "Review documentation readiness",
    ]


def test_agent5_rejects_malformed_gemini_json():
    client, _ = fake_client(text="{not valid json")

    with pytest.raises(agent5_advisory.GeminiResponseError):
        agent5_advisory.run(valid_state(), client=client, settings=SETTINGS)


def test_agent5_rejects_schema_invalid_advisory_fields():
    payload = advisory_payload()
    payload["recommended_actions"] = []
    client, _ = fake_client(payload=payload)

    with pytest.raises(ValidationError):
        agent5_advisory.run(valid_state(), client=client, settings=SETTINGS)
