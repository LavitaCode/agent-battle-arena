"""Entry point for the FastAPI application.

This file configures a basic FastAPI instance and includes a versioned API router.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import router as api_v1_router
from .core.config import settings


def get_application() -> FastAPI:
    """Create and configure a FastAPI application instance.

    Returns:
        FastAPI: The configured application.
    """
    application = FastAPI(title=settings.PROJECT_NAME)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.FRONTEND_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
    return application


app = get_application()
