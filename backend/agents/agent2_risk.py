"""Agent 2: assess shipping disruption risk from a validated Event."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.chokepoints import UnknownChokepointError, normalize_chokepoints
from backend.config import ConfigurationError, GeminiSettings, create_gemini_client
from backend.orchestrator.schema_validation import validate
from backend.prompts.agent2 import SYSTEM_INSTRUCTION, build_prompt


RISK_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "risk_assessment.schema.json"


class Agent2Error(RuntimeError):
    """Raised when Agent 2 cannot produce a trustworthy RiskAssessment."""


class GeminiResponseError(Agent2Error):
    """Raised when Gemini does not return parseable structured JSON."""


def _gemini_response_schema() -> dict[str, Any]:
    """Derive Gemini's output shape from the authoritative risk schema."""
    with RISK_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        risk_schema = json.load(schema_file)
    generated_fields = {
        "severity",
        "confidence",
        "probability",
        "affected_chokepoints",
        "estimated_duration",
        "rationale",
        "evidence",
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            name: definition
            for name, definition in risk_schema["properties"].items()
            if name in generated_fields
        },
        "required": [name for name in risk_schema["required"] if name in generated_fields],
    }


def run(
    event: dict,
    *,
    client=None,
    settings: GeminiSettings | None = None,
) -> dict:
    """Return a validated RiskAssessment derived only from a validated Event."""
    validate("event", event)

    try:
        resolved_settings = settings or GeminiSettings.from_env()
        gemini_client = client or create_gemini_client(resolved_settings)
        response = gemini_client.models.generate_content(
            model=resolved_settings.model,
            contents=build_prompt(event),
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                "response_json_schema": _gemini_response_schema(),
                "temperature": 0.1,
            },
        )
    except ConfigurationError as error:
        raise Agent2Error(str(error)) from error
    except Exception as error:
        raise Agent2Error(f"Gemini request failed: {error}") from error

    try:
        generated = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as error:
        raise GeminiResponseError("Gemini returned malformed JSON") from error
    if not isinstance(generated, dict):
        raise GeminiResponseError("Gemini response must be a JSON object")

    risk_assessment = {**generated, "run_id": event["run_id"]}
    validate("risk_assessment", risk_assessment)
    try:
        risk_assessment["affected_chokepoints"] = normalize_chokepoints(
            risk_assessment["affected_chokepoints"]
        )
    except UnknownChokepointError as error:
        raise Agent2Error(str(error)) from error
    event_chokepoints = set(event["entities"]["chokepoints_mentioned"])
    unsupported = set(risk_assessment["affected_chokepoints"]) - event_chokepoints
    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise Agent2Error(f"Affected chokepoints were not identified by Agent 1: {names}")
    source_evidence = set(event["evidence"])
    if any(item not in source_evidence for item in risk_assessment["evidence"]):
        raise Agent2Error("RiskAssessment evidence must come from the validated Event evidence")
    validate("risk_assessment", risk_assessment)
    return risk_assessment
