"""In-process broadcast hub for live notification events."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

_default_hub: Any = None


@runtime_checkable
class BroadcastHub(Protocol):
    """Publish live notification payloads for panel polling / SSE adapters."""

    def publish(self, event: dict[str, Any]) -> None: ...  # pragma: no cover

    def since(self, cursor: int = 0) -> list[dict[str, Any]]: ...  # pragma: no cover

    def pull(self) -> list[dict[str, Any]]: ...  # pragma: no cover

    def subscribe(
        self,
        callback: Callable[[dict[str, Any]], None],
    ) -> Callable[[], None]: ...  # pragma: no cover


def get_broadcast_hub() -> BroadcastHub | None:
    return _default_hub


def set_broadcast_hub(hub: BroadcastHub | None) -> BroadcastHub | None:
    global _default_hub
    _default_hub = hub
    return hub


def reset_broadcast_hub() -> None:
    set_broadcast_hub(None)


class MemoryBroadcastHub:
    """Process-local event log with optional subscriber callbacks."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._subs: list[Callable[[dict[str, Any]], None]] = []

    def publish(self, event: dict[str, Any]) -> None:
        payload = dict(event)
        self._events.append(payload)
        for callback in list(self._subs):
            try:
                callback(dict(payload))
            except Exception:
                pass

    def since(self, cursor: int = 0) -> list[dict[str, Any]]:
        try:
            start = int(cursor)
        except (TypeError, ValueError):
            start = 0
        if start < 0:
            start = 0
        return [dict(item) for item in self._events[start:]]

    def pull(self) -> list[dict[str, Any]]:
        events = [dict(item) for item in self._events]
        self._events.clear()
        return events

    def subscribe(
        self,
        callback: Callable[[dict[str, Any]], None],
    ) -> Callable[[], None]:
        self._subs.append(callback)

        def unsubscribe() -> None:
            try:
                self._subs.remove(callback)
            except ValueError:
                pass

        return unsubscribe


class CallbackBroadcastHub:
    """Fan a publish out to a callback while keeping an inner log (default memory)."""

    def __init__(
        self,
        callback: Callable[[dict[str, Any]], None],
        *,
        inner: BroadcastHub | None = None,
    ) -> None:
        self._callback = callback
        self._inner: BroadcastHub = inner or MemoryBroadcastHub()

    def publish(self, event: dict[str, Any]) -> None:
        self._inner.publish(event)
        try:
            self._callback(dict(event))
        except Exception:
            pass

    def since(self, cursor: int = 0) -> list[dict[str, Any]]:
        return self._inner.since(cursor)

    def pull(self) -> list[dict[str, Any]]:
        return self._inner.pull()

    def subscribe(
        self,
        callback: Callable[[dict[str, Any]], None],
    ) -> Callable[[], None]:
        return self._inner.subscribe(callback)
