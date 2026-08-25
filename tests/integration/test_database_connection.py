"""
Database Connection Integration Tests
=======================================
Verifies that our database setup is correct.

These tests are more important than they might appear:
- They confirm PRAGMA foreign_keys=ON is actually being executed.
- They confirm the database session can execute queries.
- They give us early warning if the SQLite configuration changes.

Without PRAGMA foreign_keys=ON, all our ON DELETE RESTRICT and
ON DELETE CASCADE constraints would be silently ignored. These tests
catch that before it causes subtle data corruption bugs.
"""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session


def test_database_session_executes_basic_query(db_session: Session) -> None:
    """Database session should be able to execute a simple query."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_sqlite_foreign_keys_are_enabled(db_session: Session) -> None:
    """
    PRAGMA foreign_keys must be ON.

    This is the most critical database configuration check.
    If this fails, all our carefully designed foreign key constraints
    (ON DELETE RESTRICT, ON DELETE CASCADE, ON DELETE SET NULL) are
    silently ignored by SQLite.
    """
    result = db_session.execute(text("PRAGMA foreign_keys"))
    value = result.scalar()
    assert value == 1, (
        "SQLite foreign key enforcement is OFF. "
        "Check that PRAGMA foreign_keys=ON is being executed on connection."
    )


def test_decimal_arithmetic_is_exact() -> None:
    """
    Python Decimal arithmetic must be exact (not floating-point).

    This is a sanity check, not a database test. We include it here as
    a reminder and documentation of why we use Decimal instead of float.

    This is the canonical example of why float is wrong for money:
        0.1 + 0.2 == 0.3  →  False with float
        Decimal('0.1') + Decimal('0.2') == Decimal('0.3')  →  True
    """
    # Float arithmetic is broken for money:
    assert 0.1 + 0.2 != 0.3  # This is True — float arithmetic is imprecise

    # Decimal arithmetic is exact:
    result = Decimal("0.1") + Decimal("0.2")
    assert result == Decimal("0.3")


def test_sqlite_version_is_available(db_session: Session) -> None:
    """Confirm we can query SQLite version information."""
    result = db_session.execute(text("SELECT sqlite_version()"))
    version = result.scalar()
    assert version is not None
    assert len(version) > 0
