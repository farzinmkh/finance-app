"""
Dashboard Router
==================
Single read-only endpoint aggregating income, expenses, top spending
categories, recent activity, and net worth for a date range.

Defaulting behavior: if date_from/date_to are omitted, the endpoint
defaults to the CURRENT calendar month (first day through last day),
computed with calendar.monthrange the same way budget spending queries
already do — this keeps "what period am I looking at" consistent across
the whole API rather than inventing a second convention here.

user_id is NEVER accepted from the client. It always comes from the
authenticated User provided by get_current_user().
"""

import calendar
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from application.use_cases.dashboard.get_dashboard import GetDashboard, GetDashboardInput
from domain.entities.user import User
from domain.exceptions import DomainValidationError
from infrastructure.database.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from infrastructure.database.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from infrastructure.database.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.dashboard import DashboardResponse

router = APIRouter()


def _current_month_range() -> tuple[date, date]:
    """First day through last day of the current calendar month."""
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return date(today.year, today.month, 1), date(today.year, today.month, last_day)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get the dashboard summary for a date range (defaults to current month)",
)
def get_dashboard(
    date_from: date | None = Query(
        default=None,
        description="Inclusive start date. Defaults to the 1st of the current month.",
    ),
    date_to: date | None = Query(
        default=None,
        description="Inclusive end date. Defaults to the last day of the current month.",
    ),
    top_categories_limit: int = Query(
        default=5, ge=1, le=20, description="Max number of top expense categories to return."
    ),
    recent_transactions_limit: int = Query(
        default=10, ge=1, le=50, description="Max number of recent transactions to return."
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """
    Provide neither date to see the current calendar month. Provide both
    to see a custom range (e.g. year-to-date, last 90 days).

    Raises:
        422 — date_from is after date_to.
    """
    if date_from is None or date_to is None:
        default_from, default_to = _current_month_range()
        date_from = date_from or default_from
        date_to = date_to or default_to

    if date_from > date_to:
        raise DomainValidationError("date_from must not be after date_to.")

    use_case = GetDashboard(
        transaction_repository=SQLAlchemyTransactionRepository(db),
        category_repository=SQLAlchemyCategoryRepository(db),
        account_repository=SQLAlchemyAccountRepository(db),
    )
    summary = use_case.execute(
        GetDashboardInput(
            user_id=current_user.id,
            date_from=date_from,
            date_to=date_to,
            top_categories_limit=top_categories_limit,
            recent_transactions_limit=recent_transactions_limit,
        )
    )
    return DashboardResponse.from_domain(summary)
