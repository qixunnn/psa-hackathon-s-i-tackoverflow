import json
from functools import lru_cache
from pathlib import Path

from pydantic import TypeAdapter

from app.models.demo import DemoArticleDefinition


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEMO_DATASET_PATH = REPOSITORY_ROOT / "data" / "demo" / "red-sea-articles.json"


class DemoArticleDataset:
    def __init__(self, articles: list[DemoArticleDefinition]) -> None:
        self._articles = articles
        self._by_replay_id = {article.replayId: article for article in articles}

    def list_articles(self) -> list[DemoArticleDefinition]:
        return list(self._articles)

    def get_article(self, replay_id: str) -> DemoArticleDefinition | None:
        return self._by_replay_id.get(replay_id)


@lru_cache
def get_demo_article_dataset() -> DemoArticleDataset:
    raw_articles = json.loads(DEMO_DATASET_PATH.read_text(encoding="utf-8"))
    articles = TypeAdapter(list[DemoArticleDefinition]).validate_python(raw_articles)
    return DemoArticleDataset(articles)
