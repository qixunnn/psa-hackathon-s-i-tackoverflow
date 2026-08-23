from functools import lru_cache
from typing import Protocol

from postgrest.exceptions import APIError
from supabase import Client

from app.db.client import get_supabase_client
from app.models.article import Article
from app.models.demo import DemoEventUpdate


class DuplicateArticleError(Exception):
    pass


class DemoReplayRepository(Protocol):
    def processed_article_ids(self, article_ids: list[str]) -> set[str]: ...

    def replay(self, article: Article, update: DemoEventUpdate) -> None: ...


class SupabaseDemoReplayRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def processed_article_ids(self, article_ids: list[str]) -> set[str]:
        if not article_ids:
            return set()
        response = (
            self._client.table("articles")
            .select("id")
            .in_("id", article_ids)
            .execute()
        )
        return {row["id"] for row in response.data}

    def replay(self, article: Article, update: DemoEventUpdate) -> None:
        parameters = {
            "p_article_id": article.id,
            "p_title": article.title,
            "p_content": article.content,
            "p_source_name": article.sourceName,
            "p_source_type": article.sourceType.value,
            "p_url": article.url,
            "p_published_at": article.publishedAt.isoformat(),
            "p_ingested_at": article.ingestedAt.isoformat(),
            "p_is_synthetic": article.isSynthetic,
            "p_content_hash": article.contentHash,
            "p_event_id": update.eventId,
            "p_event_summary": update.summary,
            "p_new_status": update.status.value,
            "p_new_severity": update.severity.value,
            "p_new_confidence": update.confidence,
            "p_development_id": update.developmentId,
            "p_development_timestamp": update.developmentTimestamp.isoformat(),
            "p_development_title": update.developmentTitle,
            "p_development_summary": update.developmentSummary,
        }
        try:
            self._client.rpc("replay_demo_article", parameters).execute()
        except APIError as error:
            if error.code == "23505":
                raise DuplicateArticleError(article.id) from error
            raise


@lru_cache
def get_demo_replay_repository() -> DemoReplayRepository:
    return SupabaseDemoReplayRepository(get_supabase_client())
