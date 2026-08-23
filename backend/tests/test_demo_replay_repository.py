from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

from supabase import Client

from app.data.demo_dataset import get_demo_article_dataset
from app.models.article import Article
from app.repositories.demo_replay_repository import SupabaseDemoReplayRepository


class FakeRequest:
    def __init__(self, data: list[dict[str, Any]] | None = None) -> None:
        self.data = data or []

    def select(self, _columns: str) -> "FakeRequest":
        return self

    def in_(self, _column: str, values: list[str]) -> "FakeRequest":
        self.data = [row for row in self.data if row["id"] in values]
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self.data)


class FakeReplayClient:
    def __init__(self) -> None:
        self.rpc_name: str | None = None
        self.rpc_parameters: dict[str, Any] | None = None

    def table(self, _name: str) -> FakeRequest:
        return FakeRequest([{"id": "ART-001"}])

    def rpc(self, name: str, parameters: dict[str, Any]) -> FakeRequest:
        self.rpc_name = name
        self.rpc_parameters = parameters
        return FakeRequest()


def test_processed_article_ids_come_from_article_persistence() -> None:
    repository = SupabaseDemoReplayRepository(cast(Client, FakeReplayClient()))

    processed = repository.processed_article_ids(["ART-001", "ART-002"])

    assert processed == {"ART-001"}


def test_replay_repository_calls_atomic_database_function() -> None:
    client = FakeReplayClient()
    repository = SupabaseDemoReplayRepository(cast(Client, client))
    definition = get_demo_article_dataset().get_article("red-sea-01")
    assert definition is not None
    article = Article(
        id=definition.articleId,
        title=definition.title,
        content=definition.content,
        sourceName=definition.sourceName,
        sourceType=definition.sourceType,
        url=definition.url,
        publishedAt=definition.publishedAt,
        ingestedAt=datetime(2026, 8, 24, 9, 0, tzinfo=timezone.utc),
        isSynthetic=True,
        contentHash="test-hash",
    )

    repository.replay(article, definition.update)

    assert client.rpc_name == "replay_demo_article"
    assert client.rpc_parameters is not None
    assert client.rpc_parameters["p_article_id"] == "ART-001"
    assert client.rpc_parameters["p_new_confidence"] == 0.41
    assert client.rpc_parameters["p_development_id"] == "DEV-RS-001"
