"""SDK exception hierarchy."""


class ArenaError(Exception):
    """Base class for all arena_sdk errors."""


class AuthError(ArenaError):
    """Authentication or session error."""


class RateLimitError(ArenaError):
    """HTTP 429 — caller exceeded rate limit."""


class NotFoundError(ArenaError):
    """Requested resource does not exist."""


class ValidationError(ArenaError):
    """Server rejected the request payload (HTTP 422 / 400)."""
