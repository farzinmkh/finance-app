"""
Update Budget Use Case
=======================
Changes the spending limit of an existing budget.

Only the amount (limit) is mutable. The category, month, and year define
the budget's identity and cannot be changed. To "move" a budget to a
different month or category, delete it and create a new one.
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.entities.budget import Budget
from domain.exceptions import NotFoundError
from domain.repositories.budget_repository import BudgetRepository


@dataclass
class UpdateBudgetInput:
    budget_id: UUID
    user_id: UUID
    amount: Decimal


class UpdateBudget:
    def __init__(self, budget_repository: BudgetRepository) -> None:
        self._budget_repo = budget_repository

    def execute(self, input_data: UpdateBudgetInput) -> Budget:
        """
        Update the budget limit.

        Raises:
            NotFoundError: budget does not exist or belongs to different user.
            DomainValidationError: new amount is zero or negative.
        """
        budget = self._budget_repo.get_by_id(input_data.budget_id, input_data.user_id)
        if budget is None:
            raise NotFoundError(f"Budget '{input_data.budget_id}' was not found.")

        # update_amount() enforces the same Decimal and positive-value rules
        # as Budget.create() — validation lives on the entity, not here.
        budget.update_amount(input_data.amount)
        return self._budget_repo.update(budget)
