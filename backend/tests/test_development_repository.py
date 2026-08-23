from types import SimpleNamespace
from typing import Any, cast

from supabase import Client

from app.repositories.development_repository import SupabaseDevelopmentRepository


class FakeDevelopmentQuery:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def select(self, _columns: str) -> "FakeDevelopmentQuery":
        return self

    def eq(self, column: str, value: str) -> "FakeDevelopmentQuery":
        self._rows = [row for row in self._rows if row[column] == value]
        return self

    def order(self, column: str, *, desc: bool) -> "FakeDevelopmentQuery":
        self._rows.sort(key=lambda row: row[column], reverse=desc)
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self._rows)


class FakeDevelopmentClient:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def table(self, _name: str) -> FakeDevelopmentQuery:
        return FakeDevelopmentQuery(self._rows.copy())


def development_row(identifier: str, timestamp: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "event_id": "EVT-001",
        "timestamp": timestamp,
        "title": "Synthetic development",
        "summary": "Synthetic development summary.",
        "source_ids": [],
        "evidence_ids": [],
        "previous_severity": "MEDIUM",
        "new_severity": "HIGH",
        "previous_confidence": 0.63,
        "new_confidence": 0.82,
    }


def test_developments_are_mapped_and_sorted_oldest_first() -> None:
    client = FakeDevelopmentClient(
        [
            development_row("DEV-RS-002", "2026-08-21T09:05:00+00:00"),
            development_row("DEV-RS-001", "2026-08-20T08:05:00+00:00"),
        ]
    )
    repository = SupabaseDevelopmentRepository(cast(Client, client))

    developments = repository.list_for_event("EVT-001")

    assert [development.id for development in developments] == [
        "DEV-RS-001",
        "DEV-RS-002",
    ]
