from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "psa-global-watch-api",
    }


def test_list_events() -> None:
    response = client.get("/api/v1/events")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"] == [
        {
            "id": "EVT-001",
            "title": "Bab el-Mandeb Security Disruption",
            "eventType": "CHOKEPOINT_DISRUPTION",
            "status": "ESCALATING",
            "severity": "HIGH",
            "confidence": 0.84,
            "primaryLocation": {
                "name": "Bab el-Mandeb",
                "latitude": 12.58,
                "longitude": 43.33,
                "region": "Red Sea",
            },
            "affectedTradeCorridors": ["Asia-Europe"],
            "lastUpdated": "2026-08-23T12:00:00Z",
            "isSynthetic": True,
        }
    ]


def test_get_event_detail() -> None:
    response = client.get("/api/v1/events/EVT-001")

    assert response.status_code == 200
    body = response.json()
    assert body["event"]["id"] == "EVT-001"
    assert body["event"]["isSynthetic"] is True
    assert body["event"]["routeExposure"]["affectedTradeCorridors"] == [
        "Asia-Europe"
    ]
    assert body["sources"] == []
    assert body["evidence"] == []
    assert body["developments"] == []
    assert body["latestScenarioRun"] is None
    assert body["latestOperationalImpact"] is None
    assert body["recommendations"] == []


def test_unknown_event_returns_404() -> None:
    response = client.get("/api/v1/events/EVT-UNKNOWN")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "EVENT_NOT_FOUND",
            "message": "The requested event could not be found.",
            "details": None,
        }
    }
