"""Configuration settings for the FastAPI application."""
import os
from pathlib import Path
from typing import List


def _load_dotenv() -> None:
    """Load local .env values when present without adding runtime dependencies."""
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


class Settings:
    """Application configuration with sensible defaults."""

    PROJECT_NAME: str = os.getenv("CQA_PROJECT_NAME", "Agent Battle Arena")
    API_V1_PREFIX: str = os.getenv("CQA_API_V1_PREFIX", "/api/v1")
    FRONTEND_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CQA_FRONTEND_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200"
        ).split(",")
        if origin.strip()
    ]
    MAX_RUN_TIME_MINUTES: int = int(os.getenv("CQA_MAX_RUN_TIME_MINUTES", "20"))
    ALLOW_EXTERNAL_NETWORK: bool = os.getenv("CQA_ALLOW_EXTERNAL_NETWORK", "false").lower() == "true"
    SANDBOX_PREFERRED_PROVIDER: str = os.getenv("CQA_SANDBOX_PREFERRED_PROVIDER", "docker")
    DOCKER_RUNNER_IMAGE: str = os.getenv("CQA_DOCKER_RUNNER_IMAGE", "cqa-runner-local:latest")
    RUN_ARTIFACTS_ROOT: str = os.getenv("CQA_RUN_ARTIFACTS_ROOT", "/tmp/cqa_runs")
    APP_DATA_ROOT: str = os.getenv(
        "CQA_APP_DATA_ROOT",
        os.path.join(os.getcwd(), "backend", "data"),
    )
    ALPHA_DB_PATH: str = os.getenv(
        "CQA_ALPHA_DB_PATH",
        os.path.join(APP_DATA_ROOT, "public_alpha.sqlite3"),
    )
    DATABASE_URL: str = os.getenv("CQA_DATABASE_URL", "")
    SESSION_COOKIE_NAME: str = os.getenv("CQA_SESSION_COOKIE_NAME", "cqa_alpha_session")
    ALPHA_REQUIRE_INVITE: bool = os.getenv("CQA_ALPHA_REQUIRE_INVITE", "true").lower() == "true"
    ENABLE_MOCK_GITHUB_AUTH: bool = os.getenv("CQA_ENABLE_MOCK_GITHUB_AUTH", "true").lower() == "true"
    DEFAULT_ALPHA_INVITE_CODE: str = os.getenv("CQA_DEFAULT_ALPHA_INVITE_CODE", "ALPHA-ACCESS")
    SESSION_TTL_HOURS: int = int(os.getenv("CQA_SESSION_TTL_HOURS", "72"))
    PUBLIC_BASE_URL: str = os.getenv("CQA_PUBLIC_BASE_URL", "http://localhost:8000")
    GITHUB_CLIENT_ID: str = os.getenv("CQA_GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("CQA_GITHUB_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI: str = os.getenv(
        "CQA_GITHUB_REDIRECT_URI",
        f"{PUBLIC_BASE_URL}{API_V1_PREFIX}/auth/github/callback",
    )
    GITHUB_AUTHORIZE_URL: str = os.getenv(
        "CQA_GITHUB_AUTHORIZE_URL",
        "https://github.com/login/oauth/authorize",
    )
    GITHUB_TOKEN_URL: str = os.getenv(
        "CQA_GITHUB_TOKEN_URL",
        "https://github.com/login/oauth/access_token",
    )
    GITHUB_USER_URL: str = os.getenv("CQA_GITHUB_USER_URL", "https://api.github.com/user")
    GITHUB_OAUTH_SCOPE: str = os.getenv("CQA_GITHUB_OAUTH_SCOPE", "read:user")


settings = Settings()
