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

    assert len(routes) == 2
    for route in routes:
        validate("route", route)


def test_vessel_validates():
    validate("vessel", load_json("vessel.json"))


def test_vessel_route_exists():
    routes = load_json("route_graph.json")
    vessel = load_json("vessel.json")

    route_ids = {route["route_id"] for route in routes}
    assert vessel["scheduled_route_id"] in route_ids


def test_baseline_includes_suez_and_bab_el_mandeb():
    routes = load_json("route_graph.json")
    baseline = next(route for route in routes if route["route_id"] == "RT-001-BASELINE")

    assert baseline["origin"] == "Rotterdam"
    assert "Suez Canal" in baseline["chokepoints"]
    assert "Bab el-Mandeb" in baseline["chokepoints"]
    assert "Strait of Hormuz" not in baseline["chokepoints"]


def test_cape_route_avoids_suez_and_bab_el_mandeb():
    routes = load_json("route_graph.json")
    cape = next(route for route in routes if route["route_id"] == "RT-002-CAPE-BYPASS")

    assert "Suez Canal" not in cape["chokepoints"]
    assert "Bab el-Mandeb" not in cape["chokepoints"]
    assert "Cape of Good Hope" in cape["waypoints"]


def test_route_measurements_are_positive_numbers():
    routes = load_json("route_graph.json")

    for route in routes:
        assert isinstance(route["distance_nm"], (int, float))
        assert isinstance(route["base_transit_days"], (int, float))
        assert route["distance_nm"] > 0
        assert route["base_transit_days"] > 0


def test_bab_el_mandeb_filter_returns_cape_bypass():
    routes = load_json("route_graph.json")

    filtered_routes = routes_avoiding_chokepoint(routes, "Bab el-Mandeb")

    assert [route["route_id"] for route in filtered_routes] == ["RT-002-CAPE-BYPASS"]


def test_cape_bypass_has_deterministic_ten_day_eta_delta():
    routes = {route["route_id"]: route for route in load_json("route_graph.json")}

    assert routes["RT-002-CAPE-BYPASS"]["distance_nm"] > routes["RT-001-BASELINE"]["distance_nm"]
    assert (
        routes["RT-002-CAPE-BYPASS"]["base_transit_days"]
        - routes["RT-001-BASELINE"]["base_transit_days"]
    ) == 10
