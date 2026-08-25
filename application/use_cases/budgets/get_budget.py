"""
Get Budget Use Case
====================
Retrieves a budget and computes its spending analytics for the month.

This use case is responsible for:
  1. Fetching the stored budget (limit only)
  2. Querying actual transaction spending for that category/month
  3. Combining them into a BudgetSummary with derived fields

The spending query is intentionally delegated to the transaction repository.
This keeps financial calculation logic in one place: the repository handles
the SQL aggregation, the use case handles the arithmetic derivations
(remaining, percentage, exceeded), and the API layer handles serialisation.
No layer duplicates another's responsibilities.
"""

from uuid import UUID

from domain.exceptions import NotFoundError
from domain.repositories.budget_repository import BudgetRepository
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.transaction_repository import TransactionRepository
from application.use_cases.budgets.budget_summary import BudgetSummary


class GetBudget:
    def __init__(
        self,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._budget_repo = budget_repository
        self._transaction_repo = transaction_repository
        self._category_repo = category_repository

    def execute(self, budget_id: UUID, user_id: UUID) -> BudgetSummary:
        """
        Return the budget with computed spending analytics.

        Raises:
            NotFoundError: budget does not exist or belongs to different user.
        """
        # ── Fetch the budget ──────────────────────────────────────────────────
        budget = self._budget_repo.get_by_id(budget_id, user_id)
        if budget is None:
            raise NotFoundError(f"Budget '{budget_id}' was not found.")

        # ── Look up the category name ─────────────────────────────────────────
        category = self._category_repo.get_by_id(budget.category_id, user_id)
        category_name = category.name if category is not None else "(deleted category)"

        # ── Compute spending from real transactions ────────────────────────────
        # This is the single source of truth for budget spending.
        # Transfer legs are excluded inside the repository method.
        spent = self._transaction_repo.get_category_month_spending(
            user_id=user_id,
            category_id=budget.category_id,
            month=budget.month,
            year=budget.year,
        )

        # ── Build the enriched summary ────────────────────────────────────────
        # BudgetSummary.build() computes remaining, percentage, is_exceeded.
        # All financial arithmetic lives in that single factory method.
        return BudgetSummary.build(budget, category_name, spent)
