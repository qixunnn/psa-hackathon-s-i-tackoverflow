"""Canned route ranking agent with computed ETA deltas."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


def run(state: dict) -> list[dict]:
    time.sleep(1)
    with (DATA_DIRECTORY / "route_graph.json").open(encoding="utf-8") as route_file:
        routes = {route["route_id"]: route for route in json.load(route_file)}
    with (DATA_DIRECTORY / "vessel.json").open(encoding="utf-8") as vessel_file:
        vessel = json.load(vessel_file)

    baseline_days = routes[vessel["scheduled_route_id"]]["base_transit_days"]
    scheduled_arrival = datetime.fromisoformat(vessel["scheduled_arrival"].replace("Z", "+00:00"))
    route_ids = [candidate["route_id"] for candidate in state["candidate_routes"]]
    scores = {
        "RT-002-FUJAIRAH-BYPASS": 0.88,
        "RT-001-BASELINE": 0.65,
    }
    ordered_route_ids = sorted(route_ids, key=lambda route_id: scores.get(route_id, 0.5), reverse=True)

    ranked_routes = []
    for rank, route_id in enumerate(ordered_route_ids, start=1):
        transit_days = routes[route_id]["base_transit_days"]
        eta_delta_days = transit_days - baseline_days
        eta = scheduled_arrival + timedelta(days=eta_delta_days)
        ranked_routes.append(
            {
                "run_id": state["run_id"],
                "route_id": route_id,
                "rank": rank,
                "score": scores.get(route_id, 0.5),
                "eta": eta.isoformat().replace("+00:00", "Z"),
                "eta_delta_days": eta_delta_days,
                "rationale": "Balances chokepoint exposure and transit time.",
            }
        )
    return ranked_routes
