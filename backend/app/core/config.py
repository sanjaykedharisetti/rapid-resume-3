"""
Application configuration using pydantic-settings.
All values are read from environment variables (with .env file support).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-to-a-random-secret-key"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./matchly.db"

    # CORS – stored as comma-separated string, parsed to list
    ALLOWED_ORIGINS: str = "*"

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 10

    # NLP
    SENTENCE_MODEL: str = "all-MiniLM-L6-v2"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
