"""
Delete Budget Use Case
=======================
Removes a budget. Does NOT affect transactions in any way.

Deleting a budget means the user no longer wants to track their spending
against a limit for that category/month. Their historical transactions
remain intact and unmodified.
"""

from uuid import UUID

from domain.exceptions import NotFoundError
from domain.repositories.budget_repository import BudgetRepository


class DeleteBudget:
    def __init__(self, budget_repository: BudgetRepository) -> None:
        self._budget_repo = budget_repository

    def execute(self, budget_id: UUID, user_id: UUID) -> None:
        """
        Raises:
            NotFoundError: budget does not exist or belongs to different user.
        """
        budget = self._budget_repo.get_by_id(budget_id, user_id)
        if budget is None:
            raise NotFoundError(f"Budget '{budget_id}' was not found.")
        self._budget_repo.delete(budget_id, user_id)
