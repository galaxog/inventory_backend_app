from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class AppState:
    settings: Any
    engine_kwargs: Dict[str, Any]
    start_time: datetime


STATE: Optional[AppState] = None


def setup_state(env_name: str | None = None) -> AppState:
    """Initialize process-local state (settings + DB engine/session)."""
    from app import app_config
    from app.models import init_engine_session

    global STATE

    env = (env_name or os.getenv("ENVIRONMENT") or "development").lower()
    settings = app_config.get_settings(env)

    engine_kwargs = dict(
        pool_pre_ping=True,
        pool_recycle=settings.SQLALCHEMY_POOL_RECYCLE,
        pool_size=settings.SQLALCHEMY_POOL_SIZE,
        max_overflow=settings.SQLALCHEMY_MAX_OVERFLOW,
    )

    # Use test db if env == testing
    db_url = settings.SQLALCHEMY_DATABASE_URI_TEST if env == "testing" else settings.SQLALCHEMY_DATABASE_URI
    if not db_url:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not configured")

    init_engine_session(db_url, testing=(env == "testing"), **engine_kwargs)

    STATE = AppState(
        settings=settings,
        engine_kwargs=engine_kwargs,
        start_time=datetime.now(),
    )
    return STATE
