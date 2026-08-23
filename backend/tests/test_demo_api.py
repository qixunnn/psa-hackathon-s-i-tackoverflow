from fastapi.testclient import TestClient

from tests.fakes import InMemoryEventRepository


def test_list_demo_articles_reflects_persistence(client: TestClient) -> None:
    response = client.get("/api/v1/demo/articles")

    assert response.status_code == 200
    assert [article["id"] for article in response.json()] == [
        "red-sea-01",
        "red-sea-02",
        "red-sea-03",
        "red-sea-04",
    ]
    assert all(article["processed"] is False for article in response.json())

    replay_response = client.post("/api/v1/demo/replay/red-sea-01")
    processed_response = client.get("/api/v1/demo/articles")

    assert replay_response.status_code == 200
    assert processed_response.json()[0]["processed"] is True
    assert all(
        article["processed"] is False
        for article in processed_response.json()[1:]
    )


def test_replay_updates_event_and_creates_development(client: TestClient) -> None:
    replay_response = client.post("/api/v1/demo/replay/red-sea-01")

    assert replay_response.status_code == 200
    assert replay_response.json() == {
        "articleId": "ART-001",
        "maritimeRelevant": True,
        "eventAction": "UPDATED",
        "eventId": "EVT-001",
        "message": "Demo article replayed successfully.",
    }

    event_response = client.get("/api/v1/events/EVT-001")
    event = event_response.json()["event"]
    assert event["confidence"] == 0.41
    assert event["severity"] == "MEDIUM"
    assert event["status"] == "MONITORING"
    assert event["lastUpdated"] == "2026-08-20T08:05:00Z"
    assert event["developmentIds"] == ["DEV-RS-001"]
    assert event_response.json()["developments"][0]["id"] == "DEV-RS-001"

    developments_response = client.get(
        "/api/v1/events/EVT-001/developments"
    )
    assert developments_response.status_code == 200
    assert developments_response.json()["items"] == [
        event_response.json()["developments"][0]
    ]


def test_duplicate_replay_returns_409_without_new_development(
    client: TestClient,
    persistence: InMemoryEventRepository,
) -> None:
    first_response = client.post("/api/v1/demo/replay/red-sea-01")
    development_count = persistence.development_count
    duplicate_response = client.post("/api/v1/demo/replay/red-sea-01")

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "error": {
            "code": "ARTICLE_DUPLICATE",
            "message": "This article has already been processed.",
            "details": {"existingArticleId": "ART-001"},
        }
    }
    assert persistence.development_count == development_count == 1


def test_unknown_demo_article_returns_404(client: TestClient) -> None:
    response = client.post("/api/v1/demo/replay/not-in-dataset")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ARTICLE_NOT_FOUND"
