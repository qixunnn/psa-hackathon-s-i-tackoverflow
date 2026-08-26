import copy
import json

import pytest

from backend.agents import agent3_route_retrieval
from backend.orchestrator.schema_validation import ValidationError, validate


def valid_event(run_id="run-3"):
    return {
        "run_id": run_id,
        "relevant": True,
        "confidence": 0.91,
        "relevance_rationale": "The event affects PSA-bound maritime shipping.",
        "summary": "A maritime chokepoint disruption was reported.",
        "entities": {
            "location": "Bab el-Mandeb",
            "event_type": "maritime security disruption",
            "date": "2026-08-25",
            "actors": ["Carrier"],
            "chokepoints_mentioned": ["Bab el-Mandeb"],
        },
        "evidence": ["Transit through a maritime chokepoint was suspended."],
        "source_url": "https://example.com/article",
        "extracted_at": "2026-08-25T10:01:00Z",
    }


def state(affected_chokepoints):
    run_id = "run-3"
    return {
        "run_id": run_id,
        "status": "retrieving_routes",
        "submitted_by": "operator",
        "submitted_at": "2026-08-25T10:00:00Z",
        "source_url": "https://example.com/article",
        "event": valid_event(run_id),
        "risk_assessment": {
            "run_id": run_id,
            "severity": "High",
            "confidence": 0.87,
            "probability": 0.72,
            "affected_chokepoints": affected_chokepoints,
            "estimated_duration": "3-5 days",
            "rationale": "The event may materially disrupt transit.",
            "evidence": ["Transit through a maritime chokepoint was suspended."],
        },
    }


def route(route_id, chokepoints, *, origin="Rotterdam", destination="PSA Singapore"):
    return {
        "route_id": route_id,
        "origin": origin,
        "destination": destination,
        "waypoints": [origin, *chokepoints, destination],
        "chokepoints": chokepoints,
        "distance_nm": 4000,
        "base_transit_days": 12,
    }


def write_graph(tmp_path, routes, *, baseline_route_id="RT-BASE"):
    graph_path = tmp_path / "route_graph.json"
    vessel_path = tmp_path / "vessel.json"
    graph_path.write_text(json.dumps(routes), encoding="utf-8")
    vessel_path.write_text(
        json.dumps(
            {
                "vessel_name": "MV Test",
                "scheduled_route_id": baseline_route_id,
                "scheduled_arrival": "2026-09-04T10:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return graph_path, vessel_path


def run_with_graph(agent_state, graph_paths):
    graph_path, vessel_path = graph_paths
    return agent3_route_retrieval.run(
        agent_state, route_graph_path=graph_path, vessel_path=vessel_path
    )


def test_bab_retrieval_retains_baseline_and_predefined_cape_alternative():
    candidates = agent3_route_retrieval.run(state(["Bab el-Mandeb"]))

    assert [candidate["route_id"] for candidate in candidates] == [
        "RT-001-BASELINE",
        "RT-002-CAPE-BYPASS",
    ]
    assert "Bab el-Mandeb" in candidates[0]["retrieved_reason"]
    assert "avoids" in candidates[1]["retrieved_reason"]

    routes = json.loads(agent3_route_retrieval.ROUTE_GRAPH_PATH.read_text(encoding="utf-8"))
    routes_by_id = {item["route_id"]: item for item in routes}
    assert "Bab el-Mandeb" in routes_by_id[candidates[0]["route_id"]]["chokepoints"]
    assert "Bab el-Mandeb" not in routes_by_id[candidates[1]["route_id"]]["chokepoints"]


def test_multiple_alternatives_use_stable_route_id_order(tmp_path):
    routes = [
        route("RT-BASE", ["Strait of Hormuz"]),
        route("RT-Z", ["Strait of Malacca"]),
        route("RT-A", []),
    ]
    candidates = run_with_graph(
        state(["Strait of Hormuz"]), write_graph(tmp_path, routes)
    )

    assert [candidate["route_id"] for candidate in candidates] == [
        "RT-BASE",
        "RT-A",
        "RT-Z",
    ]


def test_no_viable_alternative_returns_affected_baseline_only():
    candidates = agent3_route_retrieval.run(state(["Strait of Malacca"]))

    assert [candidate["route_id"] for candidate in candidates] == ["RT-001-BASELINE"]


def test_baseline_unaffected_does_not_manufacture_bypass(tmp_path):
    routes = [
        route("RT-BASE", ["Strait of Hormuz"]),
        route("RT-MALACCA", ["Strait of Malacca"]),
    ]
    candidates = run_with_graph(
        state(["Strait of Malacca"]), write_graph(tmp_path, routes)
    )

    assert [candidate["route_id"] for candidate in candidates] == ["RT-BASE"]
    assert "do not traverse" in candidates[0]["retrieved_reason"]


def test_unknown_chokepoint_reaching_agent3_fails_explicitly():
    with pytest.raises(agent3_route_retrieval.Agent3Error, match="Unrecognized chokepoint"):
        agent3_route_retrieval.run(state(["Imaginary Passage"]))


def test_recognized_chokepoint_absent_from_graph_is_not_unknown():
    agent_state = state(["Strait of Hormuz"])

    assert agent3_route_retrieval.run(agent_state) == []
    assert agent3_route_retrieval.graph_coverage(agent_state) == (
        [],
        ["Strait of Hormuz"],
    )


def test_bab_el_mandeb_plus_hormuz_retrieves_using_supported_bab():
    agent_state = state(["Bab el-Mandeb", "Strait of Hormuz"])

    candidates = agent3_route_retrieval.run(agent_state)

    assert [candidate["route_id"] for candidate in candidates] == [
        "RT-001-BASELINE",
        "RT-002-CAPE-BYPASS",
    ]
    assert agent3_route_retrieval.graph_coverage(agent_state) == (
        ["Bab el-Mandeb"],
        ["Strait of Hormuz"],
    )


@pytest.mark.parametrize(
    "malformed_graph",
    [
        {"routes": []},
        [{"route_id": "RT-BASE"}],
        [route("RT-BASE", ["Imaginary Passage"])],
    ],
)
def test_malformed_graph_data_fails_explicitly(tmp_path, malformed_graph):
    graph_paths = write_graph(tmp_path, malformed_graph)

    with pytest.raises(agent3_route_retrieval.Agent3Error):
        run_with_graph(state(["Strait of Hormuz"]), graph_paths)


def test_missing_baseline_route_reference_fails_explicitly(tmp_path):
    graph_paths = write_graph(
        tmp_path,
        [route("RT-OTHER", ["Strait of Hormuz"])],
        baseline_route_id="RT-MISSING",
    )

    with pytest.raises(agent3_route_retrieval.Agent3Error, match="missing baseline route"):
        run_with_graph(state(["Strait of Hormuz"]), graph_paths)


def test_repeated_execution_is_identical_and_does_not_mutate_input():
    agent_state = state(["Bab el-Mandeb"])
    original = copy.deepcopy(agent_state)

    first = agent3_route_retrieval.run(agent_state)
    second = agent3_route_retrieval.run(agent_state)

    assert first == second
    assert agent_state == original


def test_agent3_requires_no_gemini_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    candidates = agent3_route_retrieval.run(state(["Bab el-Mandeb"]))

    assert candidates


def test_input_risk_assessment_is_validated_before_graph_access(tmp_path):
    invalid_state = state(["Strait of Hormuz"])
    invalid_state["risk_assessment"].pop("severity")
    missing_graph = tmp_path / "does-not-exist.json"

    with pytest.raises(ValidationError):
        agent3_route_retrieval.run(
            invalid_state, route_graph_path=missing_graph, vessel_path=missing_graph
        )


def test_outputs_and_accumulated_run_validate():
    agent_state = state(["Bab el-Mandeb"])
    candidates = agent3_route_retrieval.run(agent_state)

    for candidate in candidates:
        validate("candidate_route", candidate)
    accumulated = {**agent_state, "candidate_routes": candidates, "status": "ranking"}
    validate("run", accumulated)


def test_candidate_route_ids_all_reference_graph_records():
    routes = json.loads(agent3_route_retrieval.ROUTE_GRAPH_PATH.read_text(encoding="utf-8"))
    route_ids = {item["route_id"] for item in routes}

    candidates = agent3_route_retrieval.run(state(["Bab el-Mandeb"]))

    assert {candidate["route_id"] for candidate in candidates} <= route_ids
