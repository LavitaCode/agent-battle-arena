"""Version 1 of the API.

Expose a router with basic health check endpoints. Additional endpoints can be
added here as the project evolves.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health Check", tags=["health"])
def health_check() -> dict:
    """Return a simple status payload for uptime checks."""
    return {"status": "ok"}

