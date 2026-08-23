from app.data.mock_events import MOCK_EVENT, MOCK_EVENT_DETAIL
from app.models.event import EventSummary
from app.models.responses import EventDetailResponse, EventListResponse


def list_event_summaries() -> EventListResponse:
    route_exposure = MOCK_EVENT.routeExposure
    affected_trade_corridors = (
        route_exposure.affectedTradeCorridors if route_exposure is not None else []
    )
    summary = EventSummary(
        id=MOCK_EVENT.id,
        title=MOCK_EVENT.title,
        eventType=MOCK_EVENT.eventType,
        status=MOCK_EVENT.status,
        severity=MOCK_EVENT.severity,
        confidence=MOCK_EVENT.confidence,
        primaryLocation=MOCK_EVENT.primaryLocation,
        affectedTradeCorridors=affected_trade_corridors,
        lastUpdated=MOCK_EVENT.lastUpdated,
        isSynthetic=MOCK_EVENT.isSynthetic,
    )
    return EventListResponse(items=[summary], total=1)


def get_event_detail(event_id: str) -> EventDetailResponse | None:
    if event_id != MOCK_EVENT.id:
        return None
    return MOCK_EVENT_DETAIL


# TODO: Replace mock access with persistence in a later vertical slice.
