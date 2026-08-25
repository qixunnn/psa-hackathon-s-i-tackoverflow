import json
from types import SimpleNamespace

import pytest

from backend.agents import agent4_ranking
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
        "run_id": "run-4",
        "status": "ranking",
        "submitted_by": "operator",
        "submitted_at": "2026-08-25T10:00:00Z",
        "source_url": "https://example.com/article",
        "event": {
            "run_id": "run-4",
            "relevant": True,
            "confidence": 0.91,
            "relevance_rationale": "The article affects PSA-bound maritime shipping.",
            "summary": "A chokepoint disruption was reported.",
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
            "run_id": "run-4",
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
                "run_id": "run-4",
                "route_id": "RT-001-BASELINE",
                "retrieved_reason": "Baseline route retained for comparison.",
            },
            {
                "run_id": "run-4",
                "route_id": "RT-002-FUJAIRAH-BYPASS",
                "retrieved_reason": "Avoids the affected chokepoint.",
            },
        ],
    }


def rationales_payload():
    return {
        "rationales": [
            {
                "route_id": "RT-002-FUJAIRAH-BYPASS",
                "rationale": "Avoids Hormuz risk while adding two transit days and 200 nm.",
            },
            {
                "route_id": "RT-001-BASELINE",
                "rationale": "Preserves the scheduled ETA but remains exposed to Hormuz.",
            },
        ]
    }


def test_agent4_weighted_scores_eta_math_and_gemini_rationales():
    client, models = fake_client(payload=rationales_payload())

    ranked = agent4_ranking.run(valid_state(), client=client, settings=SETTINGS)

    assert [route["route_id"] for route in ranked] == [
        "RT-002-FUJAIRAH-BYPASS",
        "RT-001-BASELINE",
    ]
    assert ranked[0]["eta_delta_days"] == 2
    assert ranked[1]["eta_delta_days"] == 0
    assert ranked[0]["score"] > ranked[1]["score"]
    assert "Avoids Hormuz risk" in ranked[0]["rationale"]
    assert models.calls[0]["config"]["response_json_schema"]["required"] == ["rationales"]
    for route in ranked:
        validate("ranked_route", route)


def test_agent4_rejects_invalid_input_before_gemini_call():
    state = valid_state()
    state["risk_assessment"].pop("severity")
    client, models = fake_client(payload=rationales_payload())

    with pytest.raises(ValidationError):
        agent4_ranking.run(state, client=client, settings=SETTINGS)
    assert models.calls == []


def test_agent4_rejects_missing_rationale_for_ranked_route():
    client, _ = fake_client(
        payload={
            "rationales": [
                {
                    "route_id": "RT-002-FUJAIRAH-BYPASS",
                    "rationale": "Avoids the affected chokepoint.",
                }
            ]
        }
    )

    with pytest.raises(agent4_ranking.GeminiResponseError):
        agent4_ranking.run(valid_state(), client=client, settings=SETTINGS)


def test_agent4_wraps_gemini_errors():
    client, _ = fake_client(error=RuntimeError("service unavailable"))

    with pytest.raises(agent4_ranking.Agent4Error, match="Gemini request failed"):
        agent4_ranking.run(valid_state(), client=client, settings=SETTINGS)
