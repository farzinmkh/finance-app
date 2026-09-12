"""
Budgets Router
================
Thin HTTP layer over the existing budget use cases.

Every response is a BudgetResponse — the enriched view (limit + computed
spent/remaining/percentage/is_exceeded), never the bare stored Budget.
CreateBudget and UpdateBudget return a plain Budget entity from the
application layer, so this router re-fetches through GetBudget immediately
after a successful create/update to build the enriched response the
client actually needs. This costs one extra read query per write, which
is a reasonable trade for never returning a budget without its spending
context (and keeps the enrichment logic in exactly one place: GetBudget).

user_id is NEVER accepted from the client. It always comes from the
authenticated User provided by get_current_user().
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from application.use_cases.budgets.create_budget import CreateBudget, CreateBudgetInput
from application.use_cases.budgets.delete_budget import DeleteBudget
from application.use_cases.budgets.get_budget import GetBudget
from application.use_cases.budgets.list_budgets import ListBudgets
from application.use_cases.budgets.update_budget import UpdateBudget, UpdateBudgetInput
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_budget_repository import (
    SQLAlchemyBudgetRepository,
)
from infrastructure.database.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from infrastructure.database.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.budgets import (
    BudgetResponse,
    CreateBudgetRequest,
    UpdateBudgetRequest,
)

router = APIRouter()


def _get_budget_use_case(db: Session) -> GetBudget:
    """Shared constructor — GetBudget needs all three repositories."""
    return GetBudget(
        budget_repository=SQLAlchemyBudgetRepository(db),
        transaction_repository=SQLAlchemyTransactionRepository(db),
        category_repository=SQLAlchemyCategoryRepository(db),
    )


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a monthly budget for an expense category",
)
def create_budget(
    payload: CreateBudgetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """
    Raises:
        404 — category not found / not owned by the current user.
        422 — category is not an expense category, or amount/month/year invalid.
        409 — a budget already exists for this category/month/year.
    """
    budget_repo = SQLAlchemyBudgetRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)

    budget = CreateBudget(
        budget_repository=budget_repo,
        category_repository=category_repo,
    ).execute(
        CreateBudgetInput(
            user_id=current_user.id,
            category_id=payload.category_id,
            amount=payload.amount,
            month=payload.month,
            year=payload.year,
        )
    )
    # New budget: spent is always 0, but GetBudget is the single source of
    # truth for how a summary is built — no need to duplicate that logic here.
    summary = _get_budget_use_case(db).execute(budget.id, current_user.id)
    return BudgetResponse.from_domain(summary)


@router.get(
    "",
    response_model=list[BudgetResponse],
    summary="List budgets for the current user",
)
def list_budgets(
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month."),
    year: int | None = Query(default=None, ge=2000, le=2100, description="Filter by year."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BudgetResponse]:
    """
    Provide both month and year to see one calendar month's budgets.
    Omit both to see every budget across all time (useful for history).
    """
    use_case = ListBudgets(
        budget_repository=SQLAlchemyBudgetRepository(db),
        transaction_repository=SQLAlchemyTransactionRepository(db),
        category_repository=SQLAlchemyCategoryRepository(db),
    )
    summaries = use_case.execute(current_user.id, month, year)
    return [BudgetResponse.from_domain(s) for s in summaries]


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
    summary="Get a single budget with its computed spending",
)
def get_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """Raises 404 if the budget does not exist or belongs to another user."""
    summary = _get_budget_use_case(db).execute(budget_id, current_user.id)
    return BudgetResponse.from_domain(summary)


@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
    summary="Update a budget's spending limit",
)
def update_budget(
    budget_id: UUID,
    payload: UpdateBudgetRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponse:
    """
    Only the amount can change — category, month, and year are immutable
    after creation (delete and recreate to move a budget).

    Raises:
        404 — budget not found or belongs to another user.
        422 — new amount is zero or negative.
    """
    budget_repo = SQLAlchemyBudgetRepository(db)
    UpdateBudget(budget_repo).execute(
        UpdateBudgetInput(
            budget_id=budget_id,
            user_id=current_user.id,
            amount=payload.amount,
        )
    )
    summary = _get_budget_use_case(db).execute(budget_id, current_user.id)
    return BudgetResponse.from_domain(summary)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a budget",
)
def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Deletes the budget only. Transactions in the category are never
    affected — this just stops tracking spending against a limit.

    Raises 404 if the budget does not exist or belongs to another user.
    """
    repo = SQLAlchemyBudgetRepository(db)
    DeleteBudget(repo).execute(budget_id, current_user.id)
