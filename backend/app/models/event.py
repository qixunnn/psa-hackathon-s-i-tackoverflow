from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import EventStatus, EventType, Severity


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Location(ContractModel):
    name: str
    latitude: float | None = None
    longitude: float | None = None
    region: str | None = None
    country: str | None = None


class RouteExposure(ContractModel):
    chokepointIds: list[str]
    affectedTradeCorridors: list[str]
    alternativeRoutes: list[str]
    explanation: str
    resolved: bool


class Event(ContractModel):
    id: str
    title: str
    eventType: EventType
    status: EventStatus
    summary: str
    primaryLocation: Location
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    firstSeen: datetime
    lastUpdated: datetime
    sourceIds: list[str]
    evidenceIds: list[str]
    developmentIds: list[str]
    routeExposure: RouteExposure | None = None
    latestScenarioRunId: str | None = None
    latestOperationalImpactId: str | None = None
    recommendationIds: list[str]
    isSynthetic: bool

    @model_validator(mode="after")
    def validate_event_dates(self) -> "Event":
        if self.firstSeen > self.lastUpdated:
            raise ValueError("firstSeen must be before or equal to lastUpdated")
        return self


class EventSummary(ContractModel):
    id: str
    title: str
    eventType: EventType
    status: EventStatus
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    primaryLocation: Location
    affectedTradeCorridors: list[str]
    lastUpdated: datetime
    isSynthetic: bool
