"""Agent 3: deterministically retrieve route references from the MVP graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.orchestrator.schema_validation import ValidationError, validate


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"
ROUTE_GRAPH_PATH = DATA_DIRECTORY / "route_graph.json"
VESSEL_PATH = DATA_DIRECTORY / "vessel.json"
TAXONOMY_PATH = DATA_DIRECTORY / "chokepoint_taxonomy.json"


class Agent3Error(RuntimeError):
    """Raised when deterministic route retrieval cannot be completed safely."""


def _read_json(path: Path, description: str) -> Any:
    try:
        with path.open(encoding="utf-8") as data_file:
            return json.load(data_file)
    except (OSError, json.JSONDecodeError) as error:
        raise Agent3Error(f"Unable to load {description}: {error}") from error


def _known_chokepoints() -> frozenset[str]:
    taxonomy = _read_json(TAXONOMY_PATH, "chokepoint taxonomy")
    if not isinstance(taxonomy, dict) or not isinstance(
        taxonomy.get("chokepoints"), dict
    ):
        raise Agent3Error("Chokepoint taxonomy must contain a chokepoints object")
    return frozenset(taxonomy["chokepoints"])


def _validated_risk(state: dict) -> dict:
    """Validate the accumulated Run and return its matching RiskAssessment."""
    validate("run", state)
    risk_assessment = state.get("risk_assessment")
    if not isinstance(risk_assessment, dict):
        raise Agent3Error("Agent 3 requires an accumulated Run with risk_assessment")
    validate("risk_assessment", risk_assessment)
    if risk_assessment["run_id"] != state["run_id"]:
        raise Agent3Error("RiskAssessment run_id does not match the accumulated Run")

    recognized = _known_chokepoints()
    invalid = sorted(
        chokepoint
        for chokepoint in risk_assessment["affected_chokepoints"]
        if chokepoint not in recognized
    )
    if invalid:
        raise Agent3Error(f"Unrecognized chokepoint(s): {', '.join(invalid)}")
    return risk_assessment


def _load_graph(
    route_graph_path: Path,
    vessel_path: Path,
) -> tuple[list[dict], dict]:
    routes = _read_json(route_graph_path, "route graph")
    if not isinstance(routes, list):
        raise Agent3Error("Route graph must be a JSON array of Route records")
    if not routes:
        raise Agent3Error("Route graph must contain at least one Route record")

    route_ids: set[str] = set()
    recognized = _known_chokepoints()
    for route in routes:
        if not isinstance(route, dict):
            raise Agent3Error("Route graph entries must be JSON objects")
        try:
            validate("route", route)
        except ValidationError as error:
            raise Agent3Error(f"Malformed route graph record: {error}") from error
        route_id = route["route_id"]
        if route_id in route_ids:
            raise Agent3Error(f"Duplicate route_id in route graph: {route_id}")
        route_ids.add(route_id)
        unknown_graph_chokepoints = sorted(set(route["chokepoints"]) - recognized)
        if unknown_graph_chokepoints:
            raise Agent3Error(
                "Route graph contains unrecognized chokepoint(s): "
                + ", ".join(unknown_graph_chokepoints)
            )

    vessel = _read_json(vessel_path, "MVP vessel record")
    if not isinstance(vessel, dict):
        raise Agent3Error("MVP vessel record must be a JSON object")
    try:
        validate("vessel", vessel)
    except ValidationError as error:
        raise Agent3Error(f"Malformed MVP vessel record: {error}") from error
    baseline_route_id = vessel["scheduled_route_id"]
    if baseline_route_id not in route_ids:
        raise Agent3Error(
            f"MVP vessel references missing baseline route: {baseline_route_id}"
        )
    return routes, vessel


def graph_coverage(
    state: dict,
    *,
    route_graph_path: Path = ROUTE_GRAPH_PATH,
    vessel_path: Path = VESSEL_PATH,
) -> tuple[list[str], list[str]]:
    """Return affected chokepoints partitioned into graph-supported/unsupported."""
    risk_assessment = _validated_risk(state)
    routes, _ = _load_graph(route_graph_path, vessel_path)
    represented = {
        chokepoint for route in routes for chokepoint in route["chokepoints"]
    }
    supported = [
        chokepoint
        for chokepoint in risk_assessment["affected_chokepoints"]
        if chokepoint in represented
    ]
    unsupported = [
        chokepoint
        for chokepoint in risk_assessment["affected_chokepoints"]
        if chokepoint not in represented
    ]
    return supported, unsupported


def run(
    state: dict,
    *,
    route_graph_path: Path = ROUTE_GRAPH_PATH,
    vessel_path: Path = VESSEL_PATH,
) -> list[dict]:
    """Return validated CandidateRoute references in deterministic route-ID order."""
    risk_assessment = _validated_risk(state)
    routes, vessel = _load_graph(route_graph_path, vessel_path)
    routes_by_id = {route["route_id"]: route for route in routes}
    baseline = routes_by_id[vessel["scheduled_route_id"]]

    represented = {
        chokepoint for route in routes for chokepoint in route["chokepoints"]
    }
    supported_affected = {
        chokepoint
        for chokepoint in risk_assessment["affected_chokepoints"]
        if chokepoint in represented
    }

    # A valid chokepoint outside the MVP graph cannot justify inventing a
    # route. The orchestrator records the unsupported value in the event log.
    if not supported_affected:
        return []

    baseline_matches = sorted(supported_affected.intersection(baseline["chokepoints"]))
    if not baseline_matches:
        selected = [
            (
                baseline,
                "Baseline route retained; graph-supported affected chokepoints "
                "do not traverse this route.",
            )
        ]
    else:
        selected = [
            (
                baseline,
                f"Baseline route retained for comparison; route {baseline['route_id']} "
                f"traverses affected chokepoint(s): {', '.join(baseline_matches)}.",
            )
        ]
        alternatives = sorted(
            (
                route
                for route in routes
                if route["route_id"] != baseline["route_id"]
                and route["origin"] == baseline["origin"]
                and route["destination"] == baseline["destination"]
                and not supported_affected.intersection(route["chokepoints"])
            ),
            key=lambda route: route["route_id"],
        )
        affected_names = ", ".join(sorted(supported_affected))
        selected.extend(
            (
                route,
                f"Route {route['route_id']} is a predefined graph alternative that "
                f"avoids affected chokepoint(s): {affected_names}.",
            )
            for route in alternatives
        )

    candidates = [
        {
            "run_id": state["run_id"],
            "route_id": route["route_id"],
            "retrieved_reason": reason,
        }
        for route, reason in selected
    ]
    for candidate in candidates:
        validate("candidate_route", candidate)
        if candidate["route_id"] not in routes_by_id:
            raise Agent3Error(
                f"CandidateRoute references missing route: {candidate['route_id']}"
            )
    return candidates
