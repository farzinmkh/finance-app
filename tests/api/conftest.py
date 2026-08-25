"""
API Test Configuration
=======================
Provides fixtures for testing FastAPI endpoints over HTTP.

Key concept — Dependency Override:
-----------------------------------
Our health endpoint uses 'Depends(get_db)' to get a database session.
In tests, we do NOT want to use the real finance.db file. Instead, we
swap the real database session for an in-memory SQLite database that:
- Is created fresh for each test (no leftover data between tests)
- Is destroyed after each test (no files left on disk)
- Does not interfere with your real development data

FastAPI provides app.dependency_overrides for exactly this purpose.
It's a dictionary: {original_dependency: replacement_function}.

TestClient:
-----------
FastAPI's TestClient (built on httpx) lets us send real HTTP requests
to the application without starting an actual web server. The requests
go through the full FastAPI stack (middleware, routing, validation,
error handling) just like a real HTTP request would.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.database.models import Base
from infrastructure.database.session import get_db
from main import app


def _make_test_session_factory():
    """
    Create an in-memory SQLite engine and session factory for testing.

    'sqlite:///:memory:' creates a database that lives only in RAM.
    It is fast, requires no cleanup, and cannot accidentally corrupt
    your development database.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Enable foreign key enforcement for the test database too.
    # Without this, our ON DELETE RESTRICT / CASCADE constraints would be
    # silently ignored during tests — defeating the purpose of having them.
    @event.listens_for(test_engine, "connect")
    def enable_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables defined in our ORM models.
    # Currently there are none, but this will be needed as models are added.
    Base.metadata.create_all(test_engine)

    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine), test_engine


@pytest.fixture()
def client() -> TestClient:
    """
    Provides a FastAPI TestClient with a clean in-memory database.

    Each test that uses this fixture gets:
    - A fresh in-memory database (no shared state between tests)
    - The real application with real routing and error handling
    - A database session injected via dependency override

    Usage in a test:
        def test_something(client: TestClient) -> None:
            response = client.get("/health")
            assert response.status_code == 200
    """
    TestSessionLocal, test_engine = _make_test_session_factory()

    def override_get_db():
        """Replacement for the real get_db that uses in-memory SQLite."""
        db: Session = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Install the override — now any route that depends on get_db
    # will receive a session from our in-memory test database instead.
    app.dependency_overrides[get_db] = override_get_db

    # Use TestClient as a context manager so it handles startup/shutdown events.
    with TestClient(app) as test_client:
        yield test_client

    # Clean up: remove the override and dispose of the engine.
    # This prevents test pollution — each test gets a clean slate.
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()
