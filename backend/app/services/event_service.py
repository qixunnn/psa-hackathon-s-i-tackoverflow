from typing import Annotated

from fastapi import Depends

from app.models.event import EventSummary
from app.models.responses import (
    DevelopmentListResponse,
    EventDetailResponse,
    EventListResponse,
)
from app.repositories.development_repository import (
    DevelopmentRepository,
    get_development_repository,
)
from app.repositories.event_repository import EventRepository, get_event_repository


class EventService:
    def __init__(
        self,
        event_repository: EventRepository,
        development_repository: DevelopmentRepository,
    ) -> None:
        self._event_repository = event_repository
        self._development_repository = development_repository

    def list_event_summaries(self) -> EventListResponse:
        events = self._event_repository.list_events()
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
        event = self._event_repository.get_event(event_id)
        if event is None:
            return None
        developments = self._development_repository.list_for_event(event_id)
        return EventDetailResponse(
            event=event,
            sources=[],
            evidence=[],
            developments=developments,
            latestScenarioRun=None,
            latestOperationalImpact=None,
            recommendations=[],
        )

    def list_developments(self, event_id: str) -> DevelopmentListResponse | None:
        if self._event_repository.get_event(event_id) is None:
            return None
        return DevelopmentListResponse(
            items=self._development_repository.list_for_event(event_id)
        )


def get_event_service(
    event_repository: Annotated[EventRepository, Depends(get_event_repository)],
    development_repository: Annotated[
        DevelopmentRepository, Depends(get_development_repository)
    ],
) -> EventService:
    return EventService(event_repository, development_repository)
