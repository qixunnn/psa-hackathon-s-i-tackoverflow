from functools import lru_cache
from typing import Any, Protocol

from supabase import Client

from app.db.client import get_supabase_client
from app.models.development import Development


DEVELOPMENT_COLUMNS = ",".join(
    (
        "id",
        "event_id",
        "timestamp",
        "title",
        "summary",
        "source_ids",
        "evidence_ids",
        "previous_severity",
        "new_severity",
        "previous_confidence",
        "new_confidence",
    )
)


class DevelopmentRepository(Protocol):
    def list_for_event(self, event_id: str) -> list[Development]: ...


class SupabaseDevelopmentRepository:
    def __init__(self, client: Client) -> None:
        self._client = client

    def list_for_event(self, event_id: str) -> list[Development]:
        response = (
            self._client.table("developments")
            .select(DEVELOPMENT_COLUMNS)
            .eq("event_id", event_id)
            .order("timestamp", desc=False)
            .execute()
        )
        return [self._development_from_row(row) for row in response.data]

    @staticmethod
    def _development_from_row(row: dict[str, Any]) -> Development:
        return Development.model_validate(
            {
                "id": row["id"],
                "eventId": row["event_id"],
                "timestamp": row["timestamp"],
                "title": row["title"],
                "summary": row["summary"],
                "sourceIds": row["source_ids"],
                "evidenceIds": row["evidence_ids"],
                "previousSeverity": row["previous_severity"],
                "newSeverity": row["new_severity"],
                "previousConfidence": row["previous_confidence"],
                "newConfidence": row["new_confidence"],
            }
        )


@lru_cache
def get_development_repository() -> DevelopmentRepository:
    return SupabaseDevelopmentRepository(get_supabase_client())
