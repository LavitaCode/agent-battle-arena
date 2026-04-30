"""Entry point for the FastAPI application.

This file configures a basic FastAPI instance and includes a versioned API router.
"""
from fastapi import FastAPI

from .api.v1 import router as api_v1_router


def get_application() -> FastAPI:
    """Create and configure a FastAPI application instance.

    Returns:
        FastAPI: The configured application.
    """
    application = FastAPI(title="Agent Battle Arena API")
    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = get_application()

