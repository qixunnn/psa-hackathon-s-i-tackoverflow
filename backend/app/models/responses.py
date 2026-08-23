from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.event import Event, EventSummary


class ResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(ResponseModel):
    status: str
    service: str


class EventListResponse(ResponseModel):
    items: list[EventSummary]
    total: int


class EventDetailResponse(ResponseModel):
    event: Event
    # TODO: Replace these placeholders with their DATA_SPEC models when those
    # resources enter the implementation scope.
    sources: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    developments: list[dict[str, Any]]
    latestScenarioRun: dict[str, Any] | None = None
    latestOperationalImpact: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]]


class ErrorDetail(ResponseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(ResponseModel):
    error: ErrorDetail
