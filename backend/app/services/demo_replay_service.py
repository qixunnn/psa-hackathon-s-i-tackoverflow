from collections.abc import Callable
from datetime import datetime, timezone
from hashlib import sha256
from typing import Annotated

from fastapi import Depends

from app.data.demo_dataset import DemoArticleDataset, get_demo_article_dataset
from app.models.article import Article
from app.models.responses import DemoArticleSummary, ProcessArticleResponse
from app.repositories.demo_replay_repository import (
    DemoReplayRepository,
    DuplicateArticleError,
    get_demo_replay_repository,
)


class DemoArticleNotFoundError(Exception):
    pass


class ArticleAlreadyProcessedError(Exception):
    def __init__(self, article_id: str) -> None:
        super().__init__(article_id)
        self.article_id = article_id


class DemoReplayService:
    def __init__(
        self,
        repository: DemoReplayRepository,
        dataset: DemoArticleDataset,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._dataset = dataset
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def list_articles(self) -> list[DemoArticleSummary]:
        articles = self._dataset.list_articles()
        processed_ids = self._repository.processed_article_ids(
            [article.articleId for article in articles]
        )
        return [
            DemoArticleSummary(
                id=article.replayId,
                title=article.title,
                publishedAt=article.publishedAt,
                processed=article.articleId in processed_ids,
            )
            for article in articles
        ]

    def replay(self, replay_id: str) -> ProcessArticleResponse:
        definition = self._dataset.get_article(replay_id)
        if definition is None:
            raise DemoArticleNotFoundError(replay_id)

        if definition.articleId in self._repository.processed_article_ids(
            [definition.articleId]
        ):
            raise ArticleAlreadyProcessedError(definition.articleId)

        content_hash = sha256(
            f"{definition.title}\n{definition.content}".encode("utf-8")
        ).hexdigest()
        article = Article(
            id=definition.articleId,
            title=definition.title,
            content=definition.content,
            sourceName=definition.sourceName,
            sourceType=definition.sourceType,
            url=definition.url,
            publishedAt=definition.publishedAt,
            ingestedAt=self._clock(),
            isSynthetic=definition.isSynthetic,
            contentHash=content_hash,
        )

        try:
            self._repository.replay(article, definition.update)
        except DuplicateArticleError as error:
            raise ArticleAlreadyProcessedError(definition.articleId) from error

        return ProcessArticleResponse(
            articleId=article.id,
            maritimeRelevant=True,
            eventAction="UPDATED",
            eventId=definition.update.eventId,
            message="Demo article replayed successfully.",
        )


def get_demo_replay_service(
    repository: Annotated[
        DemoReplayRepository, Depends(get_demo_replay_repository)
    ],
    dataset: Annotated[DemoArticleDataset, Depends(get_demo_article_dataset)],
) -> DemoReplayService:
    return DemoReplayService(repository, dataset)
