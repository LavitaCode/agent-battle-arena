"""Entry point for the FastAPI application.

This file configures a basic FastAPI instance and includes a versioned API router.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import router as api_v1_router
from .core.config import settings
from .core.metrics import increment_metric

logger = logging.getLogger(__name__)


def _warn_insecure_defaults() -> None:
    if settings.ENABLE_MOCK_GITHUB_AUTH:
        logger.warning(
            "SECURITY: CQA_ENABLE_MOCK_GITHUB_AUTH=true — any github_login is accepted. "
            "Set CQA_ENABLE_MOCK_GITHUB_AUTH=false in production."
        )
    if not settings.SESSION_COOKIE_SECURE:
        logger.warning(
            "SECURITY: CQA_SESSION_COOKIE_SECURE=false — session cookies are not Secure. "
            "Set CQA_SESSION_COOKIE_SECURE=true behind HTTPS."
        )


def get_application() -> FastAPI:
    """Create and configure a FastAPI application instance."""
    _warn_insecure_defaults()
    application = FastAPI(title=settings.PROJECT_NAME)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
    async def metrics_middleware(request, call_next):
        increment_metric("requests_total")
        return await call_next(request)

    application.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    return application


app = get_application()
