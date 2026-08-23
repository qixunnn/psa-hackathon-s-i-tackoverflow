from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from app.models.development import Development
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
    # TODO: Replace the remaining placeholders with their DATA_SPEC models when
    # those resources enter the implementation scope.
    sources: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    developments: list[Development]
    latestScenarioRun: dict[str, Any] | None = None
    latestOperationalImpact: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]]


class DevelopmentListResponse(ResponseModel):
    items: list[Development]


class DemoArticleSummary(ResponseModel):
    id: str
    title: str
    publishedAt: datetime
    processed: bool


class ProcessArticleResponse(ResponseModel):
    articleId: str
    maritimeRelevant: bool
    eventAction: Literal["CREATED", "UPDATED", "NONE"]
    eventId: str | None = None
    message: str


class ErrorDetail(ResponseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(ResponseModel):
    error: ErrorDetail
