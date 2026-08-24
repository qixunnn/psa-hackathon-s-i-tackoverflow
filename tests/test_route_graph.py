import json
from pathlib import Path

from backend.orchestrator.schema_validation import validate


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "backend" / "data"


def load_json(filename):
    with (DATA_DIRECTORY / filename).open(encoding="utf-8") as data_file:
        return json.load(data_file)


def routes_avoiding_chokepoint(routes, chokepoint):
    return [route for route in routes if chokepoint not in route["chokepoints"]]


def test_every_route_validates():
    routes = load_json("route_graph.json")

    assert len(routes) == 3
    for route in routes:
        validate("route", route)


def test_vessel_validates():
    validate("vessel", load_json("vessel.json"))


def test_vessel_route_exists():
    routes = load_json("route_graph.json")
    vessel = load_json("vessel.json")

    route_ids = {route["route_id"] for route in routes}
    assert vessel["scheduled_route_id"] in route_ids


def test_baseline_includes_hormuz():
    routes = load_json("route_graph.json")
    baseline = next(route for route in routes if route["route_id"] == "RT-001-BASELINE")

    assert "Strait of Hormuz" in baseline["chokepoints"]


def test_mitigation_route_avoids_hormuz():
    routes = load_json("route_graph.json")

    assert any("Strait of Hormuz" not in route["chokepoints"] for route in routes)


def test_route_measurements_are_positive_numbers():
    routes = load_json("route_graph.json")

    for route in routes:
        assert isinstance(route["distance_nm"], (int, float))
        assert isinstance(route["base_transit_days"], (int, float))
        assert route["distance_nm"] > 0
        assert route["base_transit_days"] > 0


def test_hormuz_filter_returns_fujairah_bypass():
    routes = load_json("route_graph.json")

    filtered_routes = routes_avoiding_chokepoint(routes, "Strait of Hormuz")

    assert [route["route_id"] for route in filtered_routes] == ["RT-002-FUJAIRAH-BYPASS"]
