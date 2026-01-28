from __future__ import annotations

from typing import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session and closes it."""
    session_factory = request.app.state.db  # scoped_session
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
