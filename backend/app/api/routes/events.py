from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.models.responses import (
    ErrorDetail,
    ErrorResponse,
    DevelopmentListResponse,
    EventDetailResponse,
    EventListResponse,
)
from app.services.event_service import EventService, get_event_service


router = APIRouter(prefix="/events", tags=["events"])


def event_not_found_response() -> JSONResponse:
    error = ErrorResponse(
        error=ErrorDetail(
            code="EVENT_NOT_FOUND",
            message="The requested event could not be found.",
            details=None,
        )
    )
    return JSONResponse(status_code=404, content=error.model_dump(mode="json"))


@router.get(
    "",
    response_model=EventListResponse,
    response_model_exclude_unset=True,
)
def list_events(
    service: Annotated[EventService, Depends(get_event_service)],
) -> EventListResponse:
    return service.list_event_summaries()


@router.get(
    "/{eventId}",
    response_model=EventDetailResponse,
    response_model_exclude_unset=True,
    responses={404: {"model": ErrorResponse}},
)
def get_event(
    eventId: str,
    service: Annotated[EventService, Depends(get_event_service)],
) -> EventDetailResponse | JSONResponse:
    event_detail = service.get_event_detail(eventId)
    if event_detail is not None:
        return event_detail

    return event_not_found_response()


@router.get(
    "/{eventId}/developments",
    response_model=DevelopmentListResponse,
    response_model_exclude_unset=True,
    responses={404: {"model": ErrorResponse}},
)
def list_event_developments(
    eventId: str,
    service: Annotated[EventService, Depends(get_event_service)],
) -> DevelopmentListResponse | JSONResponse:
    developments = service.list_developments(eventId)
    if developments is not None:
        return developments
    return event_not_found_response()
