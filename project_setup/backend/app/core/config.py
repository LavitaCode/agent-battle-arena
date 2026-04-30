"""Configuration settings for the FastAPI application.

This module defines simple configuration classes. In a real project you might
pull settings from environment variables or a .env file using Pydantic's
BaseSettings.
"""

class Settings:
    """Application configuration with sensible defaults."""

    PROJECT_NAME: str = "Agent Battle Arena"
    API_V1_PREFIX: str = "/api/v1"


settings = Settings()

