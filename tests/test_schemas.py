import pytest

from backend.orchestrator.schema_validation import ValidationError, validate


VALID_PAYLOADS = {
    "run": {
        "run_id": "run-1",
        "status": "queued",
        "submitted_by": "operator",
        "submitted_at": "2026-08-25T10:00:00Z",
        "source_url": "https://example.com/article",
    },
    "event": {
        "run_id": "run-1",
        "relevant": True,
        "confidence": 0.8,
        "relevance_rationale": "The article describes disruption at a shipping chokepoint.",
        "summary": "A shipping disruption was reported.",
        "entities": {
            "location": "Strait of Hormuz",
            "event_type": "geopolitical",
            "date": "2026-08-25",
            "actors": ["Carrier"],
            "chokepoints_mentioned": ["Strait of Hormuz"],
        },
        "evidence": ["Transit through the strait was temporarily suspended."],
        "source_url": "https://example.com/article",
        "extracted_at": "2026-08-25T10:01:00Z",
    },
    "risk_assessment": {
        "run_id": "run-1",
        "severity": "High",
        "probability": 0.7,
        "affected_chokepoints": ["Strait of Hormuz"],
        "estimated_duration": "3-5 days",
        "rationale": "The disruption affects a major shipping chokepoint.",
    },
    "route": {
        "route_id": "route-1",
        "origin": "Rotterdam",
        "destination": "PSA Singapore",
        "waypoints": ["Suez Canal"],
        "chokepoints": ["Strait of Hormuz"],
        "distance_nm": 8500.0,
        "base_transit_days": 22.0,
    },
    "candidate_route": {
        "run_id": "run-1",
        "route_id": "route-1",
        "retrieved_reason": "Avoids the affected chokepoint.",
    },
    "ranked_route": {
        "run_id": "run-1",
        "route_id": "route-1",
        "rank": 1,
        "score": 0.91,
        "eta": "2026-09-16T10:00:00Z",
        "eta_delta_days": -1.5,
        "rationale": "Lowest risk exposure among viable alternatives.",
    },
    "advisory": {
        "run_id": "run-1",
        "headline": "Monitor route disruption",
        "summary": "A possible delay may affect the scheduled voyage.",
        "recommended_actions": ["Review berth planning"],
        "confidence": 0.85,
        "operator_decision": "pending",
        "operator_comment": None,
    },
    "vessel": {
        "vessel_name": "MV Sentinel",
        "scheduled_route_id": "route-1",
        "scheduled_arrival": "2026-09-17T10:00:00Z",
    },
    "event_log_entry": {
        "run_id": "run-1",
        "timestamp": "2026-08-25T10:02:00Z",
        "agent": "agent_1_relevance",
        "message": "Article ingested.",
    },
}

INVALID_PAYLOADS = {
    entity_name: {key: value for key, value in payload.items() if key != next(iter(payload))}
    for entity_name, payload in VALID_PAYLOADS.items()
}
INVALID_PAYLOADS["run"]["status"] = "unknown"


@pytest.mark.parametrize("entity_name", VALID_PAYLOADS)
def test_valid_payloads(entity_name):
    validate(entity_name, VALID_PAYLOADS[entity_name])


@pytest.mark.parametrize("entity_name", INVALID_PAYLOADS)
def test_invalid_payloads_raise(entity_name):
    with pytest.raises(ValidationError):
        validate(entity_name, INVALID_PAYLOADS[entity_name])


def test_event_rejects_missing_relevance_rationale():
    payload = dict(VALID_PAYLOADS["event"])
    payload.pop("relevance_rationale")
    with pytest.raises(ValidationError):
        validate("event", payload)


@pytest.mark.parametrize("evidence", ["not-a-list", [], [""], [42]])
def test_event_rejects_invalid_evidence(evidence):
    payload = {**VALID_PAYLOADS["event"], "evidence": evidence}
    with pytest.raises(ValidationError):
        validate("event", payload)
