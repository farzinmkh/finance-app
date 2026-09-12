"""
Health Check Router
====================
Provides a single endpoint to verify the application is running correctly.

Why include a health check?
- Lets you immediately confirm the application started successfully.
- Verifies that the database connection works — not just the web server.
- Used by monitoring systems, load balancers, and Docker health checks
  to know whether the application is ready to receive traffic.

Endpoint: GET /health
Response: { "status": "ok", "database": "ok" }
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from infrastructure.database.session import get_db

router = APIRouter()


class HealthResponse(BaseModel):
    """
    Response schema for the health check endpoint.

    Using a Pydantic model here (rather than returning a plain dict) gives us:
    - Automatic documentation in the FastAPI /docs interface.
    - Type checking on what we return.
    - A consistent pattern with the rest of the API.
    """

    status: str
    database: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the application status and verifies database connectivity.",
)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Verify the application and its database connection are working.

    The 'db: Session = Depends(get_db)' line tells FastAPI:
    "Before running this function, call get_db() and inject the result as 'db'."
    This is FastAPI's dependency injection system.

    Returns:
        HealthResponse with:
        - status: "ok" if the application is running
        - database: "ok" if the database is reachable, "error" if not
    """
    try:
        # Execute the simplest possible query to verify the DB is reachable.
        # text() wraps a raw SQL string — required by SQLAlchemy 2.x for
        # raw SQL execution (prevents accidental injection of unsanitised SQL).
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        # If the database is unreachable, we still return HTTP 200 with
        # database: "error" rather than crashing the endpoint entirely.
        # This lets monitoring systems distinguish "app is down" from
        # "app is up but database is unreachable".
        db_status = "error"

    return HealthResponse(status="ok", database=db_status)
