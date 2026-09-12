"""
Application Entry Point
========================
Creates the FastAPI application and wires together all its components:
- Routers (URL route handlers)
- Exception handlers (domain error → HTTP response mapping)
- Startup configuration

How to run (from the project root directory):
    uvicorn main:app --reload

    --reload  → Automatically restarts when you save a file (development only)

After starting, open:
    http://127.0.0.1:8000/health    → Health check
    http://127.0.0.1:8000/docs      → Interactive API documentation (Swagger UI)
    http://127.0.0.1:8000/redoc     → Alternative API documentation

Why use a create_app() factory function?
-----------------------------------------
Instead of creating `app = FastAPI(...)` directly at module level, we wrap it
in a function. This is the Application Factory pattern.

Benefits:
- Tests can call create_app() to get a fresh application instance with
  overridden dependencies (e.g. in-memory database instead of real SQLite).
- The configuration is explicit — everything that wires up the app is
  in one function, easy to read and reason about.
- Avoids import-time side effects (the app is only created when called).

We still expose `app` at module level so uvicorn can find it with `main:app`.
"""

from fastapi import FastAPI

from config import settings
from presentation.api.error_handlers import register_error_handlers
from presentation.api.routers import (
    accounts,
    auth,
    budgets,
    categories,
    dashboard,
    health,
    transactions,
    transfers,
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function is the single place where the entire application is
    assembled. If you want to know how the app is configured, start here.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "A personal finance management API for tracking income, expenses, "
            "accounts, and transfers."
        ),
        version="0.1.0",
        # Disable docs in production if desired by setting DEBUG=False
        # For now, always enable them for ease of development.
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # --- Register Routers ---
    # Each router handles a group of related endpoints.
    # We add tags for grouping in the /docs interface.
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
    app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["Accounts"])
    app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
    app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
    app.include_router(transfers.router, prefix="/api/v1/transfers", tags=["Transfers"])
    app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

    # --- Register Exception Handlers ---
    # Maps domain exceptions (e.g. NotFoundError) to HTTP responses (e.g. 404).
    register_error_handlers(app)

    return app


# The app instance that uvicorn looks for when you run:
#   uvicorn main:app --reload
app = create_app()
