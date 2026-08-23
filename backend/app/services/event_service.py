from typing import Annotated

from fastapi import Depends

from app.models.event import EventSummary
from app.models.responses import EventDetailResponse, EventListResponse
from app.repositories.event_repository import EventRepository, get_event_repository


class EventService:
    def __init__(self, repository: EventRepository) -> None:
        self._repository = repository

    def list_event_summaries(self) -> EventListResponse:
        events = self._repository.list_events()
        summaries = []
        for event in events:
            route_exposure = event.routeExposure
            affected_trade_corridors = (
                route_exposure.affectedTradeCorridors
                if route_exposure is not None
                else []
            )
            summaries.append(
                EventSummary(
                    id=event.id,
                    title=event.title,
                    eventType=event.eventType,
                    status=event.status,
                    severity=event.severity,
                    confidence=event.confidence,
                    primaryLocation=event.primaryLocation,
                    affectedTradeCorridors=affected_trade_corridors,
                    lastUpdated=event.lastUpdated,
                    isSynthetic=event.isSynthetic,
                )
            )
        return EventListResponse(items=summaries, total=len(summaries))

    def get_event_detail(self, event_id: str) -> EventDetailResponse | None:
        event = self._repository.get_event(event_id)
        if event is None:
            return None
        return EventDetailResponse(
            event=event,
            sources=[],
            evidence=[],
            developments=[],
            latestScenarioRun=None,
            latestOperationalImpact=None,
            recommendations=[],
        )


def get_event_service(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
) -> EventService:
    return EventService(repository)
