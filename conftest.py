# conftest.py
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, declarative_base
from app.models import _ModelBase, metadata, dispose_engine, Product, InventoryUpdates

BASEDIR = Path(".")
load_dotenv(BASEDIR / ".env")
os.environ["ENVIRONMENT"] = "testing"


@pytest.fixture(scope="session")
def fastapi_app():
    from app import create_app
    return create_app("testing")


@pytest.fixture(scope="session")
def db_engine(fastapi_app, request):
    """Provides a SQLAlchemy engine for the test session."""
    # Create tables before tests
    import app.models.core
    engine = fastapi_app.state.db_engine
    base = declarative_base(cls=_ModelBase, metadata=metadata)
    base.metadata.create_all(bind=engine, checkfirst=False)

    def teardown():
        base.metadata.drop_all(bind=engine)  # Drop tables after tests
        dispose_engine()

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope="session")
def db_session_factory(fastapi_app, db_engine):
    return fastapi_app.state.db


@pytest.fixture
def fastapi_db_session(db_session_factory, request):
    session: Session = db_session_factory()

    def teardown():
        session.rollback()
        session.close()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="session")
def fastapi_client(fastapi_app):
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture
def product1(fastapi_db_session):
    from app.models import Product

    product = Product.query.filter_by(name="Test Product 1").one_or_none()

    if product is None:
        product = Product(
            name="Test Product 1",
            description="A test product",
            price=9.99,
            inventory=100
        )
        fastapi_db_session.add(product)
        fastapi_db_session.commit()
        fastapi_db_session.refresh(product)
    return product