"""
Integration Test Configuration
================================
Provides a real SQLite in-memory database for integration tests.

Integration tests vs unit tests:
---------------------------------
Unit tests:       Test logic in isolation. No database. Use fakes.
Integration tests: Test that real components work together correctly.
                  Uses a real database — but in-memory so tests are fast
                  and leave no files behind.

What integration tests verify that unit tests cannot:
- Foreign key constraints actually work (RESTRICT, CASCADE, SET NULL)
- NUMERIC(19,4) precision survives a round-trip through the database
- PRAGMA foreign_keys=ON is actually being run
- SQLAlchemy ORM mappings are correct

Fixture scope:
--------------
scope="function" means each test function gets its own fresh database.
This prevents test A from affecting test B through leftover data.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.database.models import Base


@pytest.fixture(scope="function")
def db_engine():
    """
    Creates a fresh in-memory SQLite engine for one test function.

    The engine (and therefore the database) is destroyed after the test,
    so each test always starts with an empty database and the correct schema.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Critical: enable foreign key enforcement for every connection.
    # This is the same setup as in session.py, replicated here so integration
    # tests accurately reflect the production configuration.
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables from our ORM models.
    Base.metadata.create_all(engine)

    yield engine

    # Teardown: drop all tables and close all connections.
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    """
    Provides a database session for one integration test.

    Usage in a test:
        def test_something(db_session: Session) -> None:
            db_session.execute(text("SELECT 1"))
    """
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
    )
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
