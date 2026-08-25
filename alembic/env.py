"""
Alembic Migration Environment
================================
This file is the bridge between Alembic and our application.

It tells Alembic:
1. Which database to connect to (from our settings)
2. Which models to compare against (our SQLAlchemy Base)
3. How to run migrations (online mode = against a live database)

Why import our Base here?
--------------------------
Alembic's --autogenerate feature works by comparing the current database schema
against the SQLAlchemy models registered in Base.metadata.

For autogenerate to detect your models, they must be imported before Alembic
reads Base.metadata. Importing Base here (and therefore our model files) ensures
Alembic knows about every table we have defined.

As we add model files (e.g. infrastructure/database/models.py grows to include
UserModel, AccountModel, etc.), those are automatically picked up because they
inherit from Base, and Base is imported here.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Import our application configuration and Base ──────────────────────────
# This is the key integration point. We read DATABASE_URL from our settings
# so Alembic uses the same database as the running application.
import sys
import os

# Ensure the project root is on the path so imports work when running
# Alembic from any directory (e.g. 'alembic upgrade head' from project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings  # noqa: E402
from infrastructure.database.models import Base  # noqa: E402

# ── Alembic Config Object ───────────────────────────────────────────────────
config = context.config

# Set the database URL from our application settings.
# This overrides whatever is (not) in alembic.ini, keeping configuration DRY.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from the alembic.ini [loggers] configuration.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the metadata object Alembic compares to the real database schema
# when generating migrations with --autogenerate.
target_metadata = Base.metadata


def run_migrations_online() -> None:
    """
    Run migrations against a live database connection.

    This is the standard mode for applying migrations.
    Alembic connects to the database, checks which migrations have been
    applied (stored in the 'alembic_version' table), and runs any that
    haven't been applied yet.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No connection pooling during migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # render_as_batch=True is required for SQLite when altering tables.
            # SQLite does not support ALTER COLUMN, so Alembic uses a
            # "batch" strategy: create new table, copy data, drop old table.
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
