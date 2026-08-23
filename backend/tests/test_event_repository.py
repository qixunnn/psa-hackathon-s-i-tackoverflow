from types import SimpleNamespace
from typing import Any, cast

from supabase import Client

from app.repositories.event_repository import SupabaseEventRepository


DATABASE_ROW = {
    "id": "EVT-001",
    "title": "Bab el-Mandeb Security Disruption",
    "event_type": "CHOKEPOINT_DISRUPTION",
    "status": "ESCALATING",
    "summary": (
        "Security incidents near Bab el-Mandeb have led to increasing carrier "
        "rerouting activity."
    ),
    "primary_location": {
        "name": "Bab el-Mandeb",
        "latitude": 12.58,
        "longitude": 43.33,
        "region": "Red Sea",
    },
    "severity": "HIGH",
    "confidence": 0.84,
    "first_seen": "2026-08-20T08:00:00+00:00",
    "last_updated": "2026-08-23T12:00:00+00:00",
    "source_ids": ["SRC-001", "SRC-002"],
    "evidence_ids": ["EVD-001"],
    "development_ids": ["DEV-001", "DEV-002"],
    "route_exposure": {
        "chokepointIds": ["CHK-BAB"],
        "affectedTradeCorridors": ["Asia-Europe"],
        "alternativeRoutes": ["Cape of Good Hope"],
        "explanation": (
            "The disruption may affect services using the Red Sea and Suez corridor."
        ),
        "resolved": True,
    },
    "latest_scenario_run_id": "SCN-004",
    "latest_operational_impact_id": "IMP-004",
    "recommendation_ids": ["REC-021", "REC-022"],
    "is_synthetic": True,
}


class FakeQuery:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def select(self, _columns: str) -> "FakeQuery":
        return self

    def order(self, _column: str, *, desc: bool) -> "FakeQuery":
        if desc:
            self._rows.sort(key=lambda row: row["last_updated"], reverse=True)
        return self

    def eq(self, column: str, value: str) -> "FakeQuery":
        self._rows = [row for row in self._rows if row[column] == value]
        return self

    def limit(self, count: int) -> "FakeQuery":
        self._rows = self._rows[:count]
        return self

    def execute(self) -> SimpleNamespace:
        return SimpleNamespace(data=self._rows)


class FakeSupabaseClient:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows
        self.requested_table: str | None = None

    def table(self, name: str) -> FakeQuery:
        self.requested_table = name
        return FakeQuery(self._rows.copy())


def test_repository_maps_database_row_to_event() -> None:
    client = FakeSupabaseClient([DATABASE_ROW])
    repository = SupabaseEventRepository(cast(Client, client))

    event = repository.get_event("EVT-001")

    assert client.requested_table == "events"
    assert event is not None
    assert event.id == "EVT-001"
    assert event.primaryLocation.name == "Bab el-Mandeb"
    assert event.routeExposure is not None
    assert event.routeExposure.affectedTradeCorridors == ["Asia-Europe"]
    assert event.isSynthetic is True


def test_repository_returns_none_when_event_is_missing() -> None:
    repository = SupabaseEventRepository(cast(Client, FakeSupabaseClient([])))

    assert repository.get_event("EVT-UNKNOWN") is None


def test_repository_lists_events() -> None:
    repository = SupabaseEventRepository(
        cast(Client, FakeSupabaseClient([DATABASE_ROW]))
    )

    events = repository.list_events()

    assert [event.id for event in events] == ["EVT-001"]
