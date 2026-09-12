"""
Budget Summary Output Type
===========================
BudgetSummary is the enriched output returned by GetBudget and ListBudgets.
It is an application-layer data class, not a domain entity — it combines
a stored Budget with computed analytics that require a live database query.

Defined here (rather than in a separate file) because it is only used
by budget use cases and their tests.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.entities.budget import Budget


@dataclass
class BudgetSummary:
    """
    A Budget plus all computed spending analytics for its month.

    Computed fields (never stored, always derived from real transactions):
      spent_amount     — actual total expenses for the category in the month
      remaining_amount — limit minus spent; NEGATIVE when over budget
      percentage_used  — (spent / limit) × 100; CAN exceed 100
      is_exceeded      — True only when spent > limit (not when equal)

    The negative remaining_amount is intentional: showing "-$50.00 remaining"
    is more informative than "$0.00 remaining" when over budget.
    Use is_exceeded to decide how to display this in the UI.
    """

    budget_id: UUID
    user_id: UUID
    category_id: UUID
    category_name: str       # looked up from CategoryRepository by the use case
    limit_amount: Decimal    # the stored budget limit
    month: int
    year: int
    spent_amount: Decimal    # computed from transactions
    remaining_amount: Decimal  # can be negative
    percentage_used: Decimal   # two decimal places; can exceed 100.00
    is_exceeded: bool
    created_at: datetime

    @classmethod
    def build(
        cls,
        budget: Budget,
        category_name: str,
        spent_amount: Decimal,
    ) -> "BudgetSummary":
        """
        Construct a BudgetSummary from a Budget entity and computed spending.

        All derived fields are calculated here in one place.
        This factory method is the single source of truth for how
        remaining, percentage, and is_exceeded are computed.

        The percentage calculation uses Decimal arithmetic throughout —
        never float — and rounds to 2 decimal places.
        """
        remaining = budget.amount - spent_amount

        # Guard against division by zero (the domain ensures amount > 0,
        # but being explicit here makes the calculation self-documenting).
        if budget.amount == Decimal("0"):
            percentage = Decimal("0.00")
        else:
            percentage = (spent_amount / budget.amount * Decimal("100")).quantize(
                Decimal("0.01")
            )

        return cls(
            budget_id=budget.id,
            user_id=budget.user_id,
            category_id=budget.category_id,
            category_name=category_name,
            limit_amount=budget.amount,
            month=budget.month,
            year=budget.year,
            spent_amount=spent_amount,
            remaining_amount=remaining,
            percentage_used=percentage,
            is_exceeded=spent_amount > budget.amount,
            created_at=budget.created_at,
        )
