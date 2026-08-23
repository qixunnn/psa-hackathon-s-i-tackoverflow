from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.event_repository import get_event_repository
from tests.factories import make_event
from tests.fakes import InMemoryEventRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repository = InMemoryEventRepository([make_event()])
    app.dependency_overrides[get_event_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
