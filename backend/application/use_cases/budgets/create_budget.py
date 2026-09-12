"""
Create Budget Use Case
=======================
Creates a monthly spending limit for an expense category.

Validation steps (all checked before any DB write):
  1. Category must exist and belong to the authenticated user
  2. Category must be of type 'expense' — budgeting income is not supported
  3. No existing budget for this (user, category, month, year) combination

Why check duplicate in the use case rather than relying on DB constraint?
  The DB UNIQUE constraint is the final safety net, but catching it there
  gives us an IntegrityError with a generic message. Checking explicitly
  with get_by_category_month() lets us raise a specific ConflictError with
  a clear, user-facing message before touching the database.
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.entities.budget import Budget
from domain.entities.category import CategoryType
from domain.exceptions import ConflictError, DomainValidationError, NotFoundError
from domain.repositories.budget_repository import BudgetRepository
from domain.repositories.category_repository import CategoryRepository


@dataclass
class CreateBudgetInput:
    user_id: UUID
    category_id: UUID
    amount: Decimal
    month: int
    year: int


class CreateBudget:
    def __init__(
        self,
        budget_repository: BudgetRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._budget_repo = budget_repository
        self._category_repo = category_repository

    def execute(self, input_data: CreateBudgetInput) -> Budget:
        """
        Create and persist a new budget.

        Raises:
            NotFoundError: category does not exist or belongs to different user.
            DomainValidationError: category is not an expense category, or
                                   amount/month/year are invalid (via Budget.create).
            ConflictError: a budget already exists for this category/month/year.
        """
        # ── Step 1: Verify the category ───────────────────────────────────────
        category = self._category_repo.get_by_id(
            input_data.category_id, input_data.user_id
        )
        if category is None:
            raise NotFoundError(
                f"Category '{input_data.category_id}' was not found."
            )

        # ── Step 2: Enforce expense-only rule ─────────────────────────────────
        if category.category_type != CategoryType.EXPENSE:
            raise DomainValidationError(
                f"Budgets can only be created for expense categories. "
                f"'{category.name}' is an '{category.category_type.value}' category."
            )

        # ── Step 3: Check for duplicate ───────────────────────────────────────
        existing = self._budget_repo.get_by_category_month(
            user_id=input_data.user_id,
            category_id=input_data.category_id,
            month=input_data.month,
            year=input_data.year,
        )
        if existing is not None:
            raise ConflictError(
                f"A budget for '{category.name}' already exists for "
                f"{input_data.month:02d}/{input_data.year}. "
                f"Update the existing budget instead."
            )

        # ── Step 4: Create and persist ────────────────────────────────────────
        # Budget.create() validates amount, month, and year.
        budget = Budget.create(
            user_id=input_data.user_id,
            category_id=input_data.category_id,
            amount=input_data.amount,
            month=input_data.month,
            year=input_data.year,
        )
        return self._budget_repo.save(budget)
