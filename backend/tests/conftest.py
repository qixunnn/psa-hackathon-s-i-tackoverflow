from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.demo_replay_repository import get_demo_replay_repository
from app.repositories.development_repository import get_development_repository
from app.repositories.event_repository import get_event_repository
from tests.factories import make_event
from tests.fakes import InMemoryEventRepository


@pytest.fixture
def persistence() -> InMemoryEventRepository:
    return InMemoryEventRepository([make_event()])


@pytest.fixture
def client(persistence: InMemoryEventRepository) -> Iterator[TestClient]:
    app.dependency_overrides[get_event_repository] = lambda: persistence
    app.dependency_overrides[get_development_repository] = lambda: persistence
    app.dependency_overrides[get_demo_replay_repository] = lambda: persistence

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
