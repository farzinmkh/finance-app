"""
List Budgets Use Case
======================
Returns all budgets for the user with computed spending for each.

When month and year are both provided, returns only budgets for that period.
When omitted, returns all budgets across all months (useful for history).

Each budget gets its own spending query. This is N queries for N budgets.
For personal finance (typically 5–15 budgets per month), this is fine.
"""

from uuid import UUID

from domain.repositories.budget_repository import BudgetRepository
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.transaction_repository import TransactionRepository
from application.use_cases.budgets.budget_summary import BudgetSummary


class ListBudgets:
    def __init__(
        self,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._budget_repo = budget_repository
        self._transaction_repo = transaction_repository
        self._category_repo = category_repository

    def execute(
        self,
        user_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ) -> list[BudgetSummary]:
        budgets = self._budget_repo.list_by_user(user_id, month, year)

        summaries = []
        for budget in budgets:
            category = self._category_repo.get_by_id(budget.category_id, user_id)
            category_name = category.name if category is not None else "(deleted category)"

            spent = self._transaction_repo.get_category_month_spending(
                user_id=user_id,
                category_id=budget.category_id,
                month=budget.month,
                year=budget.year,
            )
            summaries.append(BudgetSummary.build(budget, category_name, spent))

        return summaries
