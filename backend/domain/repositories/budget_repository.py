"""
Budget Repository Interface
============================
Defines the contract for budget data access.

Note on uniqueness enforcement:
    The database has UNIQUE(user_id, category_id, month, year).
    The concrete implementation raises ConflictError when a save() would
    violate this constraint. The use case checks for duplicates explicitly
    via get_by_category_month() before attempting to save, which gives a
    cleaner error message than catching a raw IntegrityError.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.budget import Budget


class BudgetRepository(ABC):

    @abstractmethod
    def get_by_id(self, budget_id: UUID, user_id: UUID) -> Budget | None:
        """
        Return the budget if it exists and belongs to user_id.
        Return None otherwise (not found OR wrong user).
        """
        ...

    @abstractmethod
    def get_by_category_month(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Budget | None:
        """
        Return the budget for this exact category/month/year combination.

        Used by CreateBudget to check for duplicates before saving.
        Returns None if no budget exists for this combination.
        """
        ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ) -> list[Budget]:
        """
        Return all budgets for the user, optionally filtered by month and year.

        When month and year are both provided, returns budgets for that
        specific calendar month. Ordered by category name (alphabetically).
        """
        ...

    @abstractmethod
    def save(self, budget: Budget) -> Budget:
        """
        Persist a new budget. Does NOT commit.

        Raises:
            ConflictError: if a budget already exists for this
                           user/category/month/year combination.
        """
        ...

    @abstractmethod
    def update(self, budget: Budget) -> Budget:
        """Persist changes to an existing budget. Does NOT commit."""
        ...

    @abstractmethod
    def delete(self, budget_id: UUID, user_id: UUID) -> None:
        """Delete a budget. Does NOT commit."""
        ...
