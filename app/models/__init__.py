from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, Optional

from sqlalchemy import (JSON, BigInteger, Boolean, CheckConstraint, Column,
                        Date, DateTime, Enum, Float, ForeignKey, Index,
                        Integer, LargeBinary, MetaData, Numeric,
                        PrimaryKeyConstraint, SmallInteger, String, Text,
                        UniqueConstraint)
from sqlalchemy import and_ as _saand
from sqlalchemy import case as _sacase
from sqlalchemy import cast as _sacast
from sqlalchemy import create_engine
from sqlalchemy import exists as _saexists
from sqlalchemy import false as _safalse
from sqlalchemy import func as _safunc
from sqlalchemy import literal as _saliteral
from sqlalchemy import not_ as _sanot
from sqlalchemy import or_ as _saor
from sqlalchemy import select as _saselect
from sqlalchemy import text as _satext
from sqlalchemy import true as _satrue
from sqlalchemy.orm import (backref, declarative_base, declared_attr,
                            relationship, scoped_session, sessionmaker)
from sqlalchemy.pool import NullPool

try:
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
except Exception:  # pragma: no cover
    UUID = JSONB = ARRAY = None  # type: ignore
# ---------- Naming conventions (Alembic-friendly) ----------
_naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=_naming_convention)


def _camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("__", "_").lower()


class _ModelBase:
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return _camel_to_snake(cls.__name__)

    id = Column(Integer, primary_key=True, autoincrement=True)


Base = declarative_base(cls=_ModelBase, metadata=metadata)


class _DB:
    engine = None  # sqlalchemy.Engine
    session: Optional[scoped_session] = None
    Model = Base

    Column = Column
    Integer = Integer
    Numeric = Numeric
    Float = Float
    String = String
    Boolean = Boolean
    DateTime = DateTime
    ForeignKey = ForeignKey
    UniqueConstraint = UniqueConstraint
    Index = Index
    PrimaryKeyConstraint = PrimaryKeyConstraint
    CheckConstraint = CheckConstraint
    JSON = JSON
    BigInteger = BigInteger
    SmallInteger = SmallInteger
    if UUID is not None:
        UUID = UUID  # type: ignore
    if JSONB is not None:
        JSONB = JSONB  # type: ignore
    if ARRAY is not None:
        ARRAY = ARRAY  # type: ign

    relationship = staticmethod(relationship)
    backref = staticmethod(backref)

    @staticmethod
    def Table(name: str, *cols, **kw):
        return _SATable(name, metadata, *cols, **kw)

    # Helpers Flask-SQLAlchemy usually exposes:
    func = _safunc
    text = staticmethod(_satext)
    and_ = staticmethod(_saand)
    or_ = staticmethod(_saor)
    not_ = staticmethod(_sanot)
    true = staticmethod(_satrue)
    false = staticmethod(_safalse)
    cast = staticmethod(_sacast)
    literal = staticmethod(_saliteral)
    case = staticmethod(_sacase)
    select = staticmethod(_saselect)
    exists = staticmethod(_saexists)


db = _DB()


# Provide Flask-SQLAlchemy-style `.query` on models
class _QueryProperty:
    def __get__(self, instance, owner):
        if db.session is None:
            raise RuntimeError(
                "DB session not initialized. Call init_engine_session() at startup."
            )
        return db.session.query(owner)


# Attach `.query` to every model class deriving from Base
setattr(Base, "query", _QueryProperty())


def init_engine_session(
    db_uri: str, testing: bool = False, **engine_kwargs: Any
) -> scoped_session:
    """Create engine + scoped_session, and attach them to `db` and `Base.query`."""

    defaults: Dict[str, Any] = dict(
        pool_pre_ping=True,
        pool_recycle=1800,
    )

    is_sqlite = db_uri.startswith("sqlite")
    if is_sqlite:
        # sqlite doesn't support the same pooling kwargs
        engine_kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": NullPool,
        }
    defaults.update(engine_kwargs or {})

    engine = create_engine(db_uri, future=True, **defaults)

    SessionFactory = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    Session = scoped_session(SessionFactory)

    db.engine = engine
    db.session = Session

    # Flask-SQLAlchemy-like: `Model.query`
    Base.query = Session.query_property()  # type: ignore[attr-defined]

    return Session


def dispose_engine() -> None:
    if db.session is not None:
        db.session.remove()
    if db.engine is not None:
        db.engine.dispose()
    db.engine = None


# Import models so Alembic sees them
from app.models.core import *  # noqa: E402,F401
