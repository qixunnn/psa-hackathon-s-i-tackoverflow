from datetime import datetime

from pydantic import Field

from app.models.enums import Severity
from app.models.event import ContractModel


class Development(ContractModel):
    id: str
    eventId: str
    timestamp: datetime
    title: str
    summary: str
    sourceIds: list[str]
    evidenceIds: list[str]
    previousSeverity: Severity | None = None
    newSeverity: Severity | None = None
    previousConfidence: float | None = Field(default=None, ge=0.0, le=1.0)
    newConfidence: float | None = Field(default=None, ge=0.0, le=1.0)
