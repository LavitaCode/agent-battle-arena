"""Check the configured public alpha storage backend."""
from __future__ import annotations

from ..core.config import settings
from ..services.alpha_store import AlphaStore


def main() -> None:
    """Initialize the alpha store and print a small readiness summary."""
    store = AlphaStore(settings.ALPHA_DB_PATH, settings.DATABASE_URL)
    templates = store.list_templates()
    storage = "postgres" if settings.DATABASE_URL.startswith(("postgres://", "postgresql://")) else "sqlite"
    print(f"storage={storage}")
    print(f"schema_version={store.get_schema_version()}")
    print(f"templates={len(templates)}")
    print(f"default_invite={store.get_invite_status(settings.DEFAULT_ALPHA_INVITE_CODE)}")


if __name__ == "__main__":
    main()
