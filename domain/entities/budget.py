"""
Budget Domain Entity
=====================
Represents a monthly spending limit for one expense category.

What a Budget stores:
  - Which category it applies to
  - The spending limit (Decimal, > 0)
  - Which month and year it covers

What a Budget does NOT store:
  - Current spending (always computed from real transactions)
  - Remaining amount (derived: limit - spent)
  - Whether it is exceeded (derived: spent > limit)

These derived values are computed in the GetBudget use case, which queries
the transaction repository for actual spending data. Storing them on the
entity would create stale data the moment any transaction changes.

Why month and year as integers rather than a date?
  A budget covers an entire calendar month, not a single point in time.
  Storing month=8, year=2024 is semantically clearer than date=2024-08-01
  and avoids any ambiguity about whether the date represents "just the
  first day" or "the entire month".

Dependency rule: imports only stdlib and domain/exceptions.py.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError


@dataclass
class Budget:
    """
    A spending limit for one expense category in one calendar month.

    The budget entity is intentionally thin — it only stores the limit.
    All calculations (spent, remaining, percentage) are performed by the
    GetBudget use case, which keeps financial logic out of the data model.

    Do not construct directly. Use Budget.create().
    """

    id: UUID
    user_id: UUID
    category_id: UUID
    amount: Decimal       # the spending limit
    month: int            # 1–12
    year: int             # 2000–2100
    created_at: datetime

    # ── Factory method ──────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user_id: UUID,
        category_id: UUID,
        amount: Decimal,
        month: int,
        year: int,
    ) -> "Budget":
        """
        Create a new Budget with validated fields.

        Does NOT verify that the category exists or belongs to the user —
        that is the use case's responsibility (it has access to the
        category repository).

        Raises:
            DomainValidationError: if amount, month, or year is invalid.
        """
        return cls(
            id=uuid4(),
            user_id=user_id,
            category_id=category_id,
            amount=cls._validate_amount(amount),
            month=cls._validate_month(month),
            year=cls._validate_year(year),
            created_at=datetime.now(timezone.utc),
        )

    # ── Mutation ─────────────────────────────────────────────────────────────

    def update_amount(self, new_amount: Decimal) -> None:
        """
        Change the spending limit.

        month, year, and category_id are immutable after creation —
        they define the budget's identity. To change them, delete and
        recreate the budget.

        Raises:
            DomainValidationError: if new_amount is invalid.
        """
        self.amount = self._validate_amount(new_amount)

    # ── Private validation ───────────────────────────────────────────────────

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        if not isinstance(amount, Decimal):
            raise DomainValidationError(
                f"Budget amount must be a Decimal, not {type(amount).__name__}. "
                "Never use float for monetary values."
            )
        if amount <= Decimal("0"):
            raise DomainValidationError(
                f"Budget amount must be greater than zero (got {amount}). "
                "A zero or negative spending limit has no financial meaning."
            )
        return amount

    @staticmethod
    def _validate_month(month: int) -> int:
        # bool is a subclass of int in Python — reject it explicitly
        if isinstance(month, bool) or not isinstance(month, int):
            raise DomainValidationError(
                f"Month must be an integer between 1 and 12 (got {month!r})."
            )
        if month < 1 or month > 12:
            raise DomainValidationError(
                f"Month must be between 1 and 12 (got {month})."
            )
        return month

    @staticmethod
    def _validate_year(year: int) -> int:
        if isinstance(year, bool) or not isinstance(year, int):
            raise DomainValidationError(
                f"Year must be an integer (got {year!r})."
            )
        if year < 2000 or year > 2100:
            raise DomainValidationError(
                f"Year must be between 2000 and 2100 (got {year})."
            )
        return year
