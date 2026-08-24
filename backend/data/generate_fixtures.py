"""Generate the static MVP route graph and vessel fixture."""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.orchestrator.schema_validation import validate


OUTPUT_DIRECTORY = Path(__file__).resolve().parent


ROUTES = [
    {
        "route_id": "RT-001-BASELINE",
        "origin": "Jebel Ali",
        "destination": "PSA Singapore",
        "waypoints": [
            "Jebel Ali",
            "Strait of Hormuz",
            "Arabian Sea",
            "Strait of Malacca",
            "PSA Singapore",
        ],
        "chokepoints": ["Strait of Hormuz", "Strait of Malacca"],
        "distance_nm": 3900,
        "base_transit_days": 11,
    },
    {
        "route_id": "RT-002-FUJAIRAH-BYPASS",
        "origin": "Jebel Ali",
        "destination": "PSA Singapore",
        "waypoints": [
            "Jebel Ali",
            "Overland Transfer to Fujairah",
            "Gulf of Oman",
            "Arabian Sea",
            "Strait of Malacca",
            "PSA Singapore",
        ],
        "chokepoints": ["Strait of Malacca"],
        "distance_nm": 4100,
        "base_transit_days": 13,
    },
    {
        "route_id": "RT-003-ESCORTED-TRANSIT",
        "origin": "Jebel Ali",
        "destination": "PSA Singapore",
        "waypoints": [
            "Jebel Ali",
            "Strait of Hormuz (convoy/escort)",
            "Arabian Sea",
            "Strait of Malacca",
            "PSA Singapore",
        ],
        "chokepoints": ["Strait of Hormuz", "Strait of Malacca"],
        "distance_nm": 3900,
        "base_transit_days": 14,
    },
]


def generate_vessel() -> dict:
    scheduled_arrival = datetime.now(timezone.utc) + timedelta(days=11)
    return {
        "vessel_name": "MV Pacific Voyager",
        "scheduled_route_id": "RT-001-BASELINE",
        "scheduled_arrival": scheduled_arrival.isoformat().replace("+00:00", "Z"),
    }


def write_json(filename: str, payload: object) -> None:
    output_path = OUTPUT_DIRECTORY / filename
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2)
        output_file.write("\n")


def main() -> None:
    for route in ROUTES:
        validate("route", route)

    vessel = generate_vessel()
    validate("vessel", vessel)

    write_json("route_graph.json", ROUTES)
    write_json("vessel.json", vessel)


if __name__ == "__main__":
    main()
