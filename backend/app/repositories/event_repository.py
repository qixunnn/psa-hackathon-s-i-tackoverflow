from functools import lru_cache
from typing import Any, Protocol

from supabase import Client

from app.db.client import get_supabase_client
from app.models.event import Event


EVENT_COLUMNS = ",".join(
    (
        "id",
        "title",
        "event_type",
        "status",
        "summary",
        "primary_location",
        "severity",
        "confidence",
        "first_seen",
        "last_updated",
        "source_ids",
        "evidence_ids",
        "development_ids",
        "route_exposure",
        "latest_scenario_run_id",
        "latest_operational_impact_id",
        "recommendation_ids",
        "is_synthetic",
    )
)


class EventRepository(Protocol):
    def list_events(self) -> list[Event]: ...

    def get_event(self, event_id: str) -> Event | None: ...


class SupabaseEventRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list_events(self) -> list[Event]:
        response = (
            self._client.table("events")
            .select(EVENT_COLUMNS)
            .order("last_updated", desc=True)
            .execute()
        )
        return [self._event_from_row(row) for row in response.data]

    def get_event(self, event_id: str) -> Event | None:
        response = (
            self._client.table("events")
            .select(EVENT_COLUMNS)
            .eq("id", event_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return self._event_from_row(response.data[0])

    @staticmethod
    def _event_from_row(row: dict[str, Any]) -> Event:
        return Event.model_validate(
            {
                "id": row["id"],
                "title": row["title"],
                "eventType": row["event_type"],
                "status": row["status"],
                "summary": row["summary"],
                "primaryLocation": row["primary_location"],
                "severity": row["severity"],
                "confidence": row["confidence"],
                "firstSeen": row["first_seen"],
                "lastUpdated": row["last_updated"],
                "sourceIds": row["source_ids"],
                "evidenceIds": row["evidence_ids"],
                "developmentIds": row["development_ids"],
                "routeExposure": row["route_exposure"],
                "latestScenarioRunId": row["latest_scenario_run_id"],
                "latestOperationalImpactId": row[
                    "latest_operational_impact_id"
                ],
                "recommendationIds": row["recommendation_ids"],
                "isSynthetic": row["is_synthetic"],
            }
        )


@lru_cache
def get_event_repository() -> EventRepository:
    return SupabaseEventRepository(get_supabase_client())
