"""Agent 5: synthesize a validated operator advisory with Gemini."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.config import ConfigurationError, GeminiSettings, create_gemini_client
from backend.orchestrator.schema_validation import validate
from backend.prompts.agent5 import SYSTEM_INSTRUCTION, build_prompt


ADVISORY_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "advisory.schema.json"


class Agent5Error(RuntimeError):
    """Raised when Agent 5 cannot produce a trustworthy Advisory."""


class GeminiResponseError(Agent5Error):
    """Raised when Gemini does not return parseable advisory JSON."""


def _gemini_response_schema() -> dict[str, Any]:
    """Derive Gemini's generated fields from the authoritative Advisory schema."""
    with ADVISORY_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        advisory_schema = json.load(schema_file)
    generated_fields = {"headline", "summary", "recommended_actions"}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            name: definition
            for name, definition in advisory_schema["properties"].items()
            if name in generated_fields
        },
        "required": [name for name in advisory_schema["required"] if name in generated_fields],
    }


def _validated_input(state: dict) -> None:
    validate("run", state)
    if not isinstance(state.get("event"), dict):
        raise Agent5Error("Agent 5 requires event")
    validate("event", state["event"])
    if not isinstance(state.get("risk_assessment"), dict):
        raise Agent5Error("Agent 5 requires risk_assessment")
    validate("risk_assessment", state["risk_assessment"])
    if not isinstance(state.get("candidate_routes"), list):
        raise Agent5Error("Agent 5 requires candidate_routes")
    for candidate in state["candidate_routes"]:
        validate("candidate_route", candidate)
    if not isinstance(state.get("ranked_routes"), list):
        raise Agent5Error("Agent 5 requires ranked_routes")
    for ranked_route in state["ranked_routes"]:
        validate("ranked_route", ranked_route)


def _advisory_confidence(state: dict) -> float:
    risk_confidence = state["risk_assessment"]["confidence"]
    if not state["ranked_routes"]:
        return round(risk_confidence, 2)
    ranking_confidence = max(route["score"] for route in state["ranked_routes"])
    return round(min(risk_confidence, ranking_confidence), 2)


def run(
    state: dict,
    *,
    client=None,
    settings: GeminiSettings | None = None,
) -> dict:
    """Return a validated Advisory synthesized from validated pipeline state."""
    _validated_input(state)
    try:
        resolved_settings = settings or GeminiSettings.from_env()
        gemini_client = client or create_gemini_client(resolved_settings)
        response = gemini_client.models.generate_content(
            model=resolved_settings.model,
            contents=build_prompt(state),
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                "response_json_schema": _gemini_response_schema(),
                "temperature": 0.2,
            },
        )
    except ConfigurationError as error:
        raise Agent5Error(str(error)) from error
    except Exception as error:
        raise Agent5Error(f"Gemini request failed: {error}") from error

    try:
        generated = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as error:
        raise GeminiResponseError("Gemini returned malformed JSON") from error
    if not isinstance(generated, dict):
        raise GeminiResponseError("Gemini response must be a JSON object")

    advisory = {
        **generated,
        "run_id": state["run_id"],
        "confidence": _advisory_confidence(state),
        "operator_decision": "pending",
        "operator_comment": None,
    }
    validate("advisory", advisory)
    return advisory
