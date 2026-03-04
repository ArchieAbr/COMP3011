"""
Application configuration and API key authentication.
"""
import os
from functools import lru_cache

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = ""
    api_key: str = "dev-key-change-in-production"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


# API Key authentication header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency that validates API key from request header.

    Usage: Depends(verify_api_key)

    Raises:
        HTTPException 401: Missing API key
        HTTPException 403: Invalid API key
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Provide X-API-Key header.",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.",
        )

    return api_key
