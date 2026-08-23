from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.responses import (
    ErrorDetail,
    ErrorResponse,
    EventDetailResponse,
    EventListResponse,
)
from app.services.event_service import get_event_detail, list_event_summaries


router = APIRouter(prefix="/events", tags=["events"])


@router.get(
    "",
    response_model=EventListResponse,
    response_model_exclude_unset=True,
)
def list_events() -> EventListResponse:
    return list_event_summaries()


@router.get(
    "/{eventId}",
    response_model=EventDetailResponse,
    response_model_exclude_unset=True,
    responses={404: {"model": ErrorResponse}},
)
def get_event(eventId: str) -> EventDetailResponse | JSONResponse:
    event_detail = get_event_detail(eventId)
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
