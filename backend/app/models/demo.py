from datetime import datetime

from pydantic import Field, model_validator

from app.models.enums import EventStatus, Severity, SourceType
from app.models.event import ContractModel


class DemoEventUpdate(ContractModel):
    eventId: str
    summary: str
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    status: EventStatus
    developmentId: str
    developmentTimestamp: datetime
    developmentTitle: str
    developmentSummary: str


class DemoArticleDefinition(ContractModel):
    replayId: str
    articleId: str
    title: str
    content: str
    sourceName: str
    sourceType: SourceType
    url: str | None = None
    publishedAt: datetime
    isSynthetic: bool
    update: DemoEventUpdate

    @model_validator(mode="after")
    def validate_synthetic_demo_data(self) -> "DemoArticleDefinition":
        if not self.isSynthetic:
            raise ValueError("Demo articles must be marked as synthetic")
        return self
