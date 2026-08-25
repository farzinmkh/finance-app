"""
Database Session Management
============================
Manages the SQLAlchemy engine and provides database sessions to the application.

Key concepts explained:
-----------------------
Engine:
    The connection to the database. Created once at startup. Think of it as
    the database server connection pool.

Session:
    A single "unit of work" with the database. Each HTTP request gets its own
    session. Changes made in a session are not visible to others until committed.
    If anything goes wrong, the session is rolled back — all changes in that
    request are cancelled together. This is how we ensure atomicity.

get_db():
    A FastAPI dependency that provides one session per request, then closes it
    when the request is done (whether it succeeded or raised an exception).
    FastAPI's dependency injection handles calling this automatically.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings


def _build_engine() -> Engine:
    """
    Create the SQLAlchemy engine from the configured DATABASE_URL.

    Why this is a function rather than a module-level call:
    - Makes it easy to create a different engine in tests (in-memory SQLite).
    - Makes the configuration logic explicit and testable.

    SQLite-specific note:
        'check_same_thread=False' is required for SQLite when used with FastAPI.
        FastAPI can process a request across multiple threads, but SQLite's
        default setting blocks cross-thread use of the same connection.
        SQLAlchemy's connection pool handles thread safety correctly, so
        disabling this check is safe in this context.
    """
    connect_args: dict = {}

    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        # echo=settings.DEBUG,  # Uncomment to log all SQL to stdout during debug
    )


engine = _build_engine()


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection: object, connection_record: object) -> None:
    """
    Enable foreign key constraint enforcement for every new SQLite connection.

    Why this is necessary:
        SQLite supports foreign keys (ON DELETE CASCADE, ON DELETE RESTRICT, etc.)
        but does NOT enforce them by default. This is a well-known SQLite quirk.
        Without this, you could delete a Category that has Transactions attached,
        and SQLite would silently allow it — ignoring all our carefully designed
        ON DELETE constraints.

    Why use an event listener instead of running it once:
        SQLAlchemy uses a connection pool. A new database connection can be
        opened at any time as the pool grows or replaces stale connections.
        This listener runs every time ANY new connection is created, so every
        connection in the pool has foreign keys enabled.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()  # type: ignore[union-attr]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# SessionLocal is a factory (a class) that creates Session objects.
#
# autocommit=False  → We control exactly when to commit. This is essential for
#                     financial operations where multiple changes must succeed
#                     together or fail together (atomicity).
#
# autoflush=False   → SQLAlchemy will not automatically send pending SQL to the
#                     database before queries. We control flushing explicitly.
#
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides one database session per request.

    Transaction management (auto-commit / auto-rollback):
    ------------------------------------------------------
    This function manages the database transaction for the entire request:

    - If the route handler returns normally → db.commit() is called.
      All changes made during the request are saved permanently.

    - If the route handler raises any exception → db.rollback() is called.
      All changes are discarded. No partial state is saved.

    - In both cases → db.close() is called in the finally block.

    Why this pattern?
        It guarantees atomicity at the request level. When the CreateTransfer
        use case (for example) updates two account balances and creates two
        transaction records, either ALL five changes commit together or NONE do.
        The use case does not need to call db.commit() — the dependency handles it.

    How to use this in a FastAPI route:

        from sqlalchemy.orm import Session
        from fastapi import Depends
        from infrastructure.database.session import get_db

        @router.post("/accounts")
        def create_account(db: Session = Depends(get_db)):
            # Write to the database here. Don't call db.commit().
            # If this function returns normally, get_db commits automatically.
            # If this function raises an exception, get_db rolls back.
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
