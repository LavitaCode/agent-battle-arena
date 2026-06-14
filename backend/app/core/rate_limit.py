"""Small in-memory fixed-window rate limiter for the alpha API."""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from time import time

from fastapi import HTTPException, Request, status

from .config import settings
from .metrics import increment_metric


@dataclass
class _Window:
    started_at: float
    count: int


_windows: dict[tuple[str, str], _Window] = {}
_lock = Lock()


def reset_rate_limiter() -> None:
    """Clear in-memory limiter state for tests and local restarts."""
    with _lock:
        _windows.clear()


def enforce_rate_limit(request: Request, group: str = "default") -> None:
    """Raise HTTP 429 when the caller exceeds the configured fixed window."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    limit = _limit_for_group(group)
    client_host = request.client.host if request.client else "unknown"
    key = (group, client_host)
    now = time()
    with _lock:
        window = _windows.get(key)
        if window is None or now - window.started_at >= 60:
            _windows[key] = _Window(started_at=now, count=1)
            return
        if window.count >= limit:
            increment_metric("rate_limit_hits_total")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        window.count += 1


def _limit_for_group(group: str) -> int:
    if group == "auth":
        return settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE
    return settings.RATE_LIMIT_REQUESTS_PER_MINUTE
