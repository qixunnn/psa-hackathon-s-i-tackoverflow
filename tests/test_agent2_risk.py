import copy
import json
from types import SimpleNamespace

import pytest

from backend.agents import agent2_risk
from backend.config import GeminiSettings
from backend.orchestrator.schema_validation import ValidationError, validate


SETTINGS = GeminiSettings(api_key="test-key", model="gemini-2.5-flash")
SOURCE_EVIDENCE = "Transit through the Strait of Hormuz was temporarily suspended."


def valid_event():
    return {
        "run_id": "run-1",
        "relevant": True,
        "confidence": 0.91,
        "relevance_rationale": "The incident affects PSA-bound maritime shipping.",
        "summary": "A carrier suspended transit through the Strait of Hormuz.",
        "entities": {
            "location": "Strait of Hormuz",
            "event_type": "maritime security disruption",
            "date": "2026-08-25",
            "actors": ["Carrier", "Regional authorities"],
            "chokepoints_mentioned": ["Strait of Hormuz"],
        },
        "evidence": [SOURCE_EVIDENCE],
        "source_url": "https://example.com/article",
        "extracted_at": "2026-08-25T10:01:00Z",
    }


def valid_payload(*, severity="High"):
    return {
        "severity": severity,
        "confidence": 0.87,
        "probability": 0.72,
        "affected_chokepoints": ["Strait of Hormuz"],
        "estimated_duration": "3-5 days",
        "rationale": "A reported transit suspension creates material delay risk.",
        "evidence": [SOURCE_EVIDENCE],
    }


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


def run_with_payload(payload):
    client, _ = fake_client(payload=payload)
    return agent2_risk.run(valid_event(), client=client, settings=SETTINGS)


def test_valid_event_returns_valid_risk_assessment():
    event = valid_event()
    client, models = fake_client(payload=valid_payload())

    result = agent2_risk.run(event, client=client, settings=SETTINGS)

    validate("risk_assessment", result)
    assert result["run_id"] == event["run_id"]
    assert models.calls[0]["model"] == "gemini-2.5-flash"
    assert models.calls[0]["config"]["response_mime_type"] == "application/json"
    assert event["summary"] in models.calls[0]["contents"]


@pytest.mark.parametrize("severity", ["Low", "Medium", "High", "Critical"])
def test_all_severity_levels_are_accepted(severity):
    assert run_with_payload(valid_payload(severity=severity))["severity"] == severity


@pytest.mark.parametrize("probability", [0, 0.5, 1])
def test_valid_probability_is_accepted(probability):
    payload = valid_payload()
    payload["probability"] = probability
    assert run_with_payload(payload)["probability"] == probability


@pytest.mark.parametrize("probability", [-0.01, 1.01])
def test_invalid_probability_is_rejected(probability):
    payload = valid_payload()
    payload["probability"] = probability
    with pytest.raises(ValidationError):
        run_with_payload(payload)


def test_valid_affected_chokepoints_are_accepted():
    result = run_with_payload(valid_payload())
    assert result["affected_chokepoints"] == ["Strait of Hormuz"]


@pytest.mark.parametrize("affected", ["Strait of Hormuz", [42]])
def test_malformed_affected_chokepoints_are_rejected(affected):
    payload = valid_payload()
    payload["affected_chokepoints"] = affected
    with pytest.raises(ValidationError):
        run_with_payload(payload)


@pytest.mark.parametrize("missing_field", ["severity", "estimated_duration", "confidence", "evidence"])
def test_missing_required_fields_are_rejected(missing_field):
    payload = valid_payload()
    payload.pop(missing_field)
    with pytest.raises(ValidationError):
        run_with_payload(payload)


def test_invalid_severity_is_rejected():
    with pytest.raises(ValidationError):
        run_with_payload(valid_payload(severity="Extreme"))


def test_malformed_gemini_json_raises_explicit_error():
    client, _ = fake_client(text="{not valid json")
    with pytest.raises(agent2_risk.GeminiResponseError):
        agent2_risk.run(valid_event(), client=client, settings=SETTINGS)


def test_gemini_api_error_is_explicit_and_wrapped():
    client, _ = fake_client(error=RuntimeError("service unavailable"))
    with pytest.raises(agent2_risk.Agent2Error, match="Gemini request failed"):
        agent2_risk.run(valid_event(), client=client, settings=SETTINGS)


def test_unvalidated_event_is_rejected_before_gemini_call():
    event = valid_event()
    event.pop("summary")
    client, models = fake_client(payload=valid_payload())
    with pytest.raises(ValidationError):
        agent2_risk.run(event, client=client, settings=SETTINGS)
    assert models.calls == []


def test_agent1_event_remains_unchanged():
    event = valid_event()
    original = copy.deepcopy(event)
    client, _ = fake_client(payload=valid_payload())
    agent2_risk.run(event, client=client, settings=SETTINGS)
    assert event == original


def test_fabricated_evidence_is_rejected():
    payload = valid_payload()
    payload["evidence"] = ["An unsupported incident occurred elsewhere."]
    with pytest.raises(agent2_risk.Agent2Error, match="validated Event evidence"):
        run_with_payload(payload)


def test_regions_are_removed_from_affected_chokepoints():
    event = valid_event()
    event["entities"]["chokepoints_mentioned"] = ["Strait of Hormuz", "Bab el-Mandeb"]
    payload = valid_payload()
    payload["affected_chokepoints"] = [
        "Strait of Hormuz",
        "Red Sea",
        "Bab el-Mandeb",
        "Gulf of Oman",
    ]
    client, _ = fake_client(payload=payload)

    result = agent2_risk.run(event, client=client, settings=SETTINGS)

    assert result["affected_chokepoints"] == ["Strait of Hormuz", "Bab el-Mandeb"]


def test_agent2_chokepoint_alias_normalization_is_deterministic():
    payload = valid_payload()
    payload["affected_chokepoints"] = ["hormuz strait"]

    assert run_with_payload(payload)["affected_chokepoints"] == ["Strait of Hormuz"]


def test_agent2_canonicalizes_bab_el_mandeb_strait_alias():
    event = valid_event()
    event["entities"]["chokepoints_mentioned"] = ["Bab el-Mandeb"]
    payload = valid_payload()
    payload["affected_chokepoints"] = ["Bab el-Mandeb strait"]
    client, _ = fake_client(payload=payload)

    result = agent2_risk.run(event, client=client, settings=SETTINGS)

    assert result["affected_chokepoints"] == ["Bab el-Mandeb"]


def test_agent2_rejects_unrecognized_chokepoint():
    payload = valid_payload()
    payload["affected_chokepoints"] = ["Imaginary Passage"]

    with pytest.raises(agent2_risk.Agent2Error, match="Unrecognized chokepoint"):
        run_with_payload(payload)


def test_agent2_rejects_known_chokepoint_not_identified_by_agent1():
    payload = valid_payload()
    payload["affected_chokepoints"] = ["Strait of Malacca"]

    with pytest.raises(agent2_risk.Agent2Error, match="not identified by Agent 1"):
        run_with_payload(payload)


def test_indeterminate_duration_is_valid_when_event_has_no_numeric_support():
    payload = valid_payload()
    payload["estimated_duration"] = (
        "Indeterminate; expected to persist until a political agreement is reached"
    )

    result = run_with_payload(payload)

    assert result["estimated_duration"].startswith("Indeterminate")
