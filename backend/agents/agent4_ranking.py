"""Agent 4: rank candidate routes with deterministic scores and ETA math."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from backend.config import ConfigurationError, GeminiSettings, create_gemini_client
from backend.orchestrator.schema_validation import ValidationError, validate
from backend.prompts.agent4 import SYSTEM_INSTRUCTION, build_prompt


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"

SEVERITY_FACTORS = {
    "Low": 0.25,
    "Medium": 0.5,
    "High": 0.75,
    "Critical": 1.0,
}

WEIGHTS = {
    "risk": 0.75,
    "transit": 0.15,
    "distance": 0.1,
}


class Agent4Error(RuntimeError):
    """Raised when Agent 4 cannot produce trustworthy RankedRoute records."""


class GeminiResponseError(Agent4Error):
    """Raised when Gemini does not return parseable rationale JSON."""


def _read_json(path: Path, description: str) -> Any:
    try:
        with path.open(encoding="utf-8") as data_file:
            return json.load(data_file)
    except (OSError, json.JSONDecodeError) as error:
        raise Agent4Error(f"Unable to load {description}: {error}") from error


def _gemini_response_schema(route_ids: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "rationales": {
                "type": "array",
                "minItems": len(route_ids),
                "maxItems": len(route_ids),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "route_id": {"type": "string", "enum": route_ids},
                        "rationale": {"type": "string", "minLength": 1},
                    },
                    "required": ["route_id", "rationale"],
                },
            }
        },
        "required": ["rationales"],
    }


def _load_route_data() -> tuple[dict[str, dict], dict]:
    routes = _read_json(DATA_DIRECTORY / "route_graph.json", "route graph")
    if not isinstance(routes, list):
        raise Agent4Error("Route graph must be a JSON array of Route records")
    routes_by_id = {}
    for route in routes:
        if not isinstance(route, dict):
            raise Agent4Error("Route graph entries must be JSON objects")
        try:
            validate("route", route)
        except ValidationError as error:
            raise Agent4Error(f"Malformed route graph record: {error}") from error
        routes_by_id[route["route_id"]] = route

    vessel = _read_json(DATA_DIRECTORY / "vessel.json", "MVP vessel record")
    if not isinstance(vessel, dict):
        raise Agent4Error("MVP vessel record must be a JSON object")
    try:
        validate("vessel", vessel)
    except ValidationError as error:
        raise Agent4Error(f"Malformed MVP vessel record: {error}") from error
    if vessel["scheduled_route_id"] not in routes_by_id:
        raise Agent4Error(f"MVP vessel references missing baseline route: {vessel['scheduled_route_id']}")
    return routes_by_id, vessel


def _validated_inputs(state: dict) -> tuple[dict, list[dict]]:
    validate("run", state)
    risk_assessment = state.get("risk_assessment")
    if not isinstance(risk_assessment, dict):
        raise Agent4Error("Agent 4 requires risk_assessment")
    validate("risk_assessment", risk_assessment)
    if risk_assessment["run_id"] != state["run_id"]:
        raise Agent4Error("RiskAssessment run_id does not match the accumulated Run")

    candidate_routes = state.get("candidate_routes")
    if not isinstance(candidate_routes, list):
        raise Agent4Error("Agent 4 requires candidate_routes")
    for candidate in candidate_routes:
        validate("candidate_route", candidate)
        if candidate["run_id"] != state["run_id"]:
            raise Agent4Error("CandidateRoute run_id does not match the accumulated Run")
    return risk_assessment, candidate_routes


def _normalize_inverse(value: float, values: list[float]) -> float:
    minimum = min(values)
    maximum = max(values)
    if maximum == minimum:
        return 1.0
    return 1 - ((value - minimum) / (maximum - minimum))


def _score_routes(
    state: dict,
    risk_assessment: dict,
    candidate_routes: list[dict],
    routes_by_id: dict[str, dict],
    vessel: dict,
) -> tuple[list[dict], list[dict]]:
    baseline = routes_by_id[vessel["scheduled_route_id"]]
    baseline_days = baseline["base_transit_days"]
    scheduled_arrival = datetime.fromisoformat(vessel["scheduled_arrival"].replace("Z", "+00:00"))
    affected_chokepoints = set(risk_assessment["affected_chokepoints"])
    severity_factor = SEVERITY_FACTORS[risk_assessment["severity"]]
    probability = risk_assessment["probability"]

    route_ids = [candidate["route_id"] for candidate in candidate_routes]
    unknown_route_ids = sorted(route_id for route_id in route_ids if route_id not in routes_by_id)
    if unknown_route_ids:
        raise Agent4Error(f"CandidateRoute references missing route(s): {', '.join(unknown_route_ids)}")

    route_records = [routes_by_id[route_id] for route_id in route_ids]
    transit_values = [route["base_transit_days"] for route in route_records]
    distance_values = [route["distance_nm"] for route in route_records]
    scored = []
    context_routes = []

    for route in route_records:
        exposed = bool(affected_chokepoints.intersection(route["chokepoints"]))
        risk_score = 1 - (probability * severity_factor if exposed else 0)
        transit_score = _normalize_inverse(route["base_transit_days"], transit_values)
        distance_score = _normalize_inverse(route["distance_nm"], distance_values)
        score = (
            WEIGHTS["risk"] * risk_score
            + WEIGHTS["transit"] * transit_score
            + WEIGHTS["distance"] * distance_score
        )
        eta_delta_days = route["base_transit_days"] - baseline_days
        eta = scheduled_arrival + timedelta(days=eta_delta_days)
        partial = {
            "run_id": state["run_id"],
            "route_id": route["route_id"],
            "score": round(score, 4),
            "eta": eta.isoformat().replace("+00:00", "Z"),
            "eta_delta_days": eta_delta_days,
        }
        scored.append(partial)
        context_routes.append({
            **partial,
            "origin": route["origin"],
            "destination": route["destination"],
            "distance_nm": route["distance_nm"],
            "base_transit_days": route["base_transit_days"],
            "chokepoints": route["chokepoints"],
            "risk_exposed": exposed,
            "risk_score": round(risk_score, 4),
            "transit_score": round(transit_score, 4),
            "distance_score": round(distance_score, 4),
        })

    ordered = sorted(scored, key=lambda item: (-item["score"], item["eta_delta_days"], item["route_id"]))
    for rank, route in enumerate(ordered, start=1):
        route["rank"] = rank
    context_by_id = {route["route_id"]: route for route in context_routes}
    ordered_context = [{**context_by_id[route["route_id"]], "rank": route["rank"]} for route in ordered]
    return ordered, ordered_context


def _generate_rationales(
    ranking_context: dict,
    route_ids: list[str],
    *,
    client=None,
    settings: GeminiSettings | None = None,
) -> dict[str, str]:
    try:
        resolved_settings = settings or GeminiSettings.from_env()
        gemini_client = client or create_gemini_client(resolved_settings)
        response = gemini_client.models.generate_content(
            model=resolved_settings.model,
            contents=build_prompt(ranking_context),
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "response_mime_type": "application/json",
                "response_json_schema": _gemini_response_schema(route_ids),
                "temperature": 0.1,
            },
        )
    except ConfigurationError as error:
        raise Agent4Error(str(error)) from error
    except Exception as error:
        raise Agent4Error(f"Gemini request failed: {error}") from error

    try:
        generated = json.loads(response.text)
    except (TypeError, json.JSONDecodeError) as error:
        raise GeminiResponseError("Gemini returned malformed JSON") from error
    if not isinstance(generated, dict) or not isinstance(generated.get("rationales"), list):
        raise GeminiResponseError("Gemini response must contain a rationales array")

    rationales = {}
    for item in generated["rationales"]:
        if not isinstance(item, dict):
            raise GeminiResponseError("Each rationale must be a JSON object")
        route_id = item.get("route_id")
        rationale = item.get("rationale")
        if route_id not in route_ids or not isinstance(rationale, str) or not rationale.strip():
            raise GeminiResponseError("Gemini returned an invalid route rationale")
        if route_id in rationales:
            raise GeminiResponseError(f"Gemini returned duplicate rationale for {route_id}")
        rationales[route_id] = rationale.strip()
    missing = sorted(set(route_ids) - set(rationales))
    if missing:
        raise GeminiResponseError(f"Gemini omitted rationale(s): {', '.join(missing)}")
    return rationales


def run(
    state: dict,
    *,
    client=None,
    settings: GeminiSettings | None = None,
) -> list[dict]:
    """Return validated RankedRoute records from deterministic scoring plus Gemini rationale text."""
    risk_assessment, candidate_routes = _validated_inputs(state)
    routes_by_id, vessel = _load_route_data()
    scored_routes, context_routes = _score_routes(
        state, risk_assessment, candidate_routes, routes_by_id, vessel
    )
    route_ids = [route["route_id"] for route in scored_routes]
    rationales = _generate_rationales(
        {
            "run_id": state["run_id"],
            "weights": WEIGHTS,
            "risk_assessment": risk_assessment,
            "ranked_routes": context_routes,
        },
        route_ids,
        client=client,
        settings=settings,
    )

    ranked_routes = [
        {
            **route,
            "rationale": rationales[route["route_id"]],
        }
        for route in scored_routes
    ]
    for route in ranked_routes:
        validate("ranked_route", route)
    return ranked_routes
