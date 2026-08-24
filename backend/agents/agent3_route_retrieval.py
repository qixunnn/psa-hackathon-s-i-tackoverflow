"""Deterministic route retrieval agent."""

import json
import time
from pathlib import Path


ROUTE_GRAPH_PATH = Path(__file__).resolve().parents[1] / "data" / "route_graph.json"


def run(state: dict) -> list[dict]:
    time.sleep(1)
    with ROUTE_GRAPH_PATH.open(encoding="utf-8") as route_file:
        routes = json.load(route_file)

    affected_chokepoints = set(state["risk_assessment"]["affected_chokepoints"])
    selected_routes = [
        route
        for route in routes
        if route["route_id"] == "RT-001-BASELINE"
        or not affected_chokepoints.intersection(route["chokepoints"])
    ]
    return [
        {
            "run_id": state["run_id"],
            "route_id": route["route_id"],
            "retrieved_reason": (
                "Baseline route retained for comparison."
                if route["route_id"] == "RT-001-BASELINE"
                else "Avoids affected chokepoints."
            ),
        }
        for route in selected_routes
    ]
