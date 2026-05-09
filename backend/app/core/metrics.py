"""In-memory operational metrics for the closed alpha."""
from __future__ import annotations

from threading import Lock


_DEFAULT_COUNTERS = {
    "requests_total": 0,
    "rate_limit_hits_total": 0,
    "battles_queued_total": 0,
    "battles_completed_total": 0,
    "battles_failed_total": 0,
}
_counters = dict(_DEFAULT_COUNTERS)
_lock = Lock()


def increment_metric(name: str, value: int = 1) -> None:
    """Increment a named counter."""
    with _lock:
        _counters[name] = _counters.get(name, 0) + value


def snapshot_metrics() -> dict[str, int]:
    """Return a copy of the current metric counters."""
    with _lock:
        return dict(_counters)


def reset_metrics() -> None:
    """Reset counters for tests and local smoke checks."""
    with _lock:
        _counters.clear()
        _counters.update(_DEFAULT_COUNTERS)
