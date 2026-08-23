from app.models.event import Event


class InMemoryEventRepository:
    def __init__(self, events: list[Event]) -> None:
        self._events = {event.id: event for event in events}

    def list_events(self) -> list[Event]:
        return list(self._events.values())

    def get_event(self, event_id: str) -> Event | None:
        return self._events.get(event_id)
