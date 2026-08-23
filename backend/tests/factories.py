from datetime import datetime, timezone

from app.models.enums import EventStatus, EventType, Severity
from app.models.event import Event, Location, RouteExposure


def make_event() -> Event:
    return Event(
        id="EVT-001",
        title="Bab el-Mandeb Security Disruption",
        eventType=EventType.CHOKEPOINT_DISRUPTION,
        status=EventStatus.ESCALATING,
        summary=(
            "Security incidents near Bab el-Mandeb have led to increasing carrier "
            "rerouting activity."
        ),
        primaryLocation=Location(
            name="Bab el-Mandeb",
            latitude=12.58,
            longitude=43.33,
            region="Red Sea",
        ),
        severity=Severity.HIGH,
        confidence=0.84,
        firstSeen=datetime(2026, 8, 20, 8, 0, tzinfo=timezone.utc),
        lastUpdated=datetime(2026, 8, 23, 12, 0, tzinfo=timezone.utc),
        sourceIds=["SRC-001", "SRC-002"],
        evidenceIds=["EVD-001"],
        developmentIds=[],
        routeExposure=RouteExposure(
            chokepointIds=["CHK-BAB"],
            affectedTradeCorridors=["Asia-Europe"],
            alternativeRoutes=["Cape of Good Hope"],
            explanation=(
                "The disruption may affect services using the Red Sea and Suez "
                "corridor."
            ),
            resolved=True,
        ),
        latestScenarioRunId="SCN-004",
        latestOperationalImpactId="IMP-004",
        recommendationIds=["REC-021", "REC-022"],
        isSynthetic=True,
    )
