from datetime import datetime, timezone

import pytest

from app.data.demo_dataset import get_demo_article_dataset
from app.services.demo_replay_service import (
    ArticleAlreadyProcessedError,
    DemoReplayService,
)
from tests.factories import make_event
from tests.fakes import InMemoryEventRepository


def make_service(
    repository: InMemoryEventRepository,
) -> DemoReplayService:
    return DemoReplayService(
        repository,
        get_demo_article_dataset(),
        clock=lambda: datetime(2026, 8, 24, 9, 0, tzinfo=timezone.utc),
    )


def test_replay_service_applies_deterministic_progression() -> None:
    repository = InMemoryEventRepository([make_event()])
    service = make_service(repository)

    for replay_id in (
        "red-sea-01",
        "red-sea-02",
        "red-sea-03",
        "red-sea-04",
    ):
        service.replay(replay_id)

    event = repository.get_event("EVT-001")
    developments = repository.list_for_event("EVT-001")
    assert event is not None
    assert event.confidence == 0.91
    assert event.severity.value == "HIGH"
    assert event.status.value == "ESCALATING"
    assert event.developmentIds == [
        "DEV-RS-001",
        "DEV-RS-002",
        "DEV-RS-003",
        "DEV-RS-004",
    ]
    assert [development.newConfidence for development in developments] == [
        0.41,
        0.63,
        0.82,
        0.91,
    ]


def test_replay_service_rejects_duplicate_without_mutation() -> None:
    repository = InMemoryEventRepository([make_event()])
    service = make_service(repository)
    service.replay("red-sea-01")

    with pytest.raises(ArticleAlreadyProcessedError):
        service.replay("red-sea-01")

    assert repository.development_count == 1
