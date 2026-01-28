from __future__ import annotations

import logging
import os
from datetime import timedelta
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class InvalidConfigurationError(Exception):
    """Specified an invalid Configuration class"""


class Settings(BaseSettings):
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    # BCRYPT_LOG_ROUNDS: int = int(os.getenv("BCRYPT_LOG_ROUNDS", 12))
    # MIN_PASSWORD_LEN: int = int(os.getenv("MIN_PASSWORD_LEN", 8))
    #
    # # JWT
    # JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    # JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    # JWT_ACCESS_TOKEN_EXPIRES: timedelta = Field(
    #     default=timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 4)))
    # )
    # JWT_REFRESH_TOKEN_EXPIRES: timedelta = Field(
    #     default=timedelta(hours=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_HOURS", 48)))
    # )

    # DB
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    SQLALCHEMY_DATABASE_URI_TEST: str = os.getenv(
        "SQLALCHEMY_DATABASE_URI_TEST", "sqlite+pysqlite:///./test.db"
    )

    # Connection pool
    SQLALCHEMY_POOL_SIZE: int = int(os.getenv("SQLALCHEMY_POOL_SIZE", 5))
    SQLALCHEMY_MAX_OVERFLOW: int = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10))
    SQLALCHEMY_POOL_RECYCLE: int = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", 1800))

    class Config:
        env_file = ".env"

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def _ensure_db_uri(cls, v):
        # allow empty in some environments; fail later if used
        return v or ""


class DevelopmentConfig(Settings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: int = logging.DEBUG


class TestingConfig(Settings):
    ENVIRONMENT: str = "testing"
    TESTING: bool = True


class ProductionConfig(Settings):
    ENVIRONMENT: str = "production"
    DEBUG: bool = False


CONFIG_BY_ENV = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def _get_config(env: str | None = None) -> Settings:
    env_name = (env or os.getenv("ENVIRONMENT", "development")).lower()
    try:
        cfg_cls = CONFIG_BY_ENV[env_name]
        os.environ["ENVIRONMENT"] = env_name
        return cfg_cls()
    except KeyError as e:
        raise InvalidConfigurationError(f"{env} is not a valid configuration") from e


@lru_cache
def get_settings(env: str | None = None) -> Settings:
    """Process-level cached settings getter."""
    return _get_config(env)
