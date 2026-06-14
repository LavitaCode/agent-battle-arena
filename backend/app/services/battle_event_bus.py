"""In-process pub/sub bus for battle status events (SSE feed)."""
from __future__ import annotations

import threading
from collections import defaultdict
from typing import Iterator


class BattleEventBus:
    """Thread-safe, in-process pub/sub for battle status transitions.

    Producers call publish(); consumers iterate over subscribe().
    Each subscriber gets its own queue so slow consumers don't block others.
    Closed battles automatically drain their queues via a sentinel value.
    """

    _SENTINEL = object()

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # battle_id → list of queue.Queue
        self._subs: dict[str, list[object]] = defaultdict(list)

    def publish(self, battle_id: str, event: dict) -> None:
        """Broadcast an event dict to all subscribers of this battle."""
        import queue as _queue

        with self._lock:
            queues = list(self._subs.get(battle_id, []))
        for q in queues:
            try:
                q.put_nowait(event)  # type: ignore[union-attr]
            except Exception:
                pass

    def close(self, battle_id: str) -> None:
        """Signal all subscribers that no more events will arrive."""
        import queue as _queue

        with self._lock:
            queues = list(self._subs.get(battle_id, []))
        for q in queues:
            try:
                q.put_nowait(self._SENTINEL)  # type: ignore[union-attr]
            except Exception:
                pass

    def subscribe(self, battle_id: str) -> Iterator[dict]:
        """Yield events for battle_id until the battle is closed."""
        import queue as _queue

        q: _queue.Queue = _queue.Queue(maxsize=64)
        with self._lock:
            self._subs[battle_id].append(q)
        try:
            while True:
                item = q.get(timeout=30)
                if item is self._SENTINEL:
                    return
                yield item
        except _queue.Empty:
            return
        finally:
            with self._lock:
                try:
                    self._subs[battle_id].remove(q)
                except ValueError:
                    pass


# Module-level singleton shared by the FastAPI app
_bus = BattleEventBus()


def get_bus() -> BattleEventBus:
    return _bus
