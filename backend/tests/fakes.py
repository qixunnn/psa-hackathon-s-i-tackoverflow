from app.models.article import Article
from app.models.demo import DemoEventUpdate
from app.models.development import Development
from app.models.event import Event
from app.repositories.demo_replay_repository import DuplicateArticleError


class InMemoryEventRepository:
    def __init__(self, events: list[Event]) -> None:
        self._events = {event.id: event for event in events}
        self._articles: dict[str, Article] = {}
        self._developments: dict[str, Development] = {}

    def list_events(self) -> list[Event]:
        return list(self._events.values())

    def get_event(self, event_id: str) -> Event | None:
        return self._events.get(event_id)

    def list_for_event(self, event_id: str) -> list[Development]:
        return sorted(
            (
                development
                for development in self._developments.values()
                if development.eventId == event_id
            ),
            key=lambda development: development.timestamp,
        )

    def processed_article_ids(self, article_ids: list[str]) -> set[str]:
        return set(article_ids).intersection(self._articles)

    def replay(self, article: Article, update: DemoEventUpdate) -> None:
        if article.id in self._articles:
            raise DuplicateArticleError(article.id)

        event = self._events[update.eventId]
        development = Development(
            id=update.developmentId,
            eventId=update.eventId,
            timestamp=update.developmentTimestamp,
            title=update.developmentTitle,
            summary=update.developmentSummary,
            sourceIds=[],
            evidenceIds=[],
            previousSeverity=event.severity,
            newSeverity=update.severity,
            previousConfidence=event.confidence,
            newConfidence=update.confidence,
        )
        updated_event = event.model_copy(
            update={
                "summary": update.summary,
                "status": update.status,
                "severity": update.severity,
                "confidence": update.confidence,
                "lastUpdated": update.developmentTimestamp,
                "developmentIds": [*event.developmentIds, development.id],
            }
        )

        self._articles[article.id] = article
        self._developments[development.id] = development
        self._events[event.id] = updated_event

    @property
    def development_count(self) -> int:
        return len(self._developments)
