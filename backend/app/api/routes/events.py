from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.models.responses import (
    ErrorDetail,
    ErrorResponse,
    EventDetailResponse,
    EventListResponse,
)
from app.services.event_service import EventService, get_event_service


router = APIRouter(prefix="/events", tags=["events"])


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

    error = ErrorResponse(
        error=ErrorDetail(
            code="EVENT_NOT_FOUND",
            message="The requested event could not be found.",
            details=None,
        )
    )
    return JSONResponse(status_code=404, content=error.model_dump(mode="json"))
