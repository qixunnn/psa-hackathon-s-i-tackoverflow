from app.services.event_service import EventService
from tests.factories import make_event
from tests.fakes import InMemoryEventRepository


def test_list_event_summaries_uses_persisted_events() -> None:
    repository = InMemoryEventRepository([make_event()])
    service = EventService(repository, repository)

    response = service.list_event_summaries()

    assert response.total == 1
    assert response.items[0].id == "EVT-001"
    assert response.items[0].affectedTradeCorridors == ["Asia-Europe"]
    assert response.items[0].isSynthetic is True


def test_get_event_detail_wraps_current_slice_collections() -> None:
    repository = InMemoryEventRepository([make_event()])
    service = EventService(repository, repository)

    response = service.get_event_detail("EVT-001")

    assert response is not None
    assert response.event.id == "EVT-001"
    assert response.sources == []
    assert response.evidence == []
    assert response.developments == []
    assert response.latestScenarioRun is None
    assert response.latestOperationalImpact is None
    assert response.recommendations == []


def test_get_event_detail_returns_none_for_unknown_event() -> None:
    repository = InMemoryEventRepository([make_event()])
    service = EventService(repository, repository)

    assert service.get_event_detail("EVT-UNKNOWN") is None
