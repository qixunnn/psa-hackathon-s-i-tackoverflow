from datetime import datetime

from app.models.enums import SourceType
from app.models.event import ContractModel


class Article(ContractModel):
    id: str
    title: str
    content: str
    sourceName: str
    sourceType: SourceType
    url: str | None = None
    publishedAt: datetime
    ingestedAt: datetime
    isSynthetic: bool
    contentHash: str | None = None
