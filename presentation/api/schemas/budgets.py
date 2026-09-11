"""
Budget API Schemas
====================
Request/response models for the budgets endpoints.

Design notes:

1. The response schema wraps BudgetSummary (the application-layer type),
   not the bare Budget entity — every budget response includes the
   computed spent/remaining/percentage/is_exceeded fields. There is no
   "thin" budget response; a budget without its spending context isn't
   useful to a client.

2. category_type is NOT accepted on create/update. The category itself
   already carries its type; CreateBudget enforces server-side that the
   referenced category is an expense category (see create_budget.py).

3. month/year are immutable after creation, matching Budget.update_amount()
   — only `amount` can change. UpdateBudgetRequest therefore has a single
   field.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from application.use_cases.budgets.budget_summary import BudgetSummary


# ── Request schemas ───────────────────────────────────────────────────────────


class CreateBudgetRequest(BaseModel):
    category_id: UUID = Field(..., description="Must be an expense category.")
    amount: Decimal = Field(..., gt=0, description="Spending limit for the month.")
    month: int = Field(..., ge=1, le=12, description="1–12.")
    year: int = Field(..., ge=2000, le=2100, description="2000–2100.")


class UpdateBudgetRequest(BaseModel):
    """Only the spending limit can be changed. category/month/year are immutable."""

    amount: Decimal = Field(..., gt=0, description="New spending limit.")


# ── Response schema ───────────────────────────────────────────────────────────


class BudgetResponse(BaseModel):
    """
    A budget plus its computed spending analytics for the month.

    remaining_amount can be negative (over budget) — that's intentional,
    see BudgetSummary's docstring. Use is_exceeded to drive UI state
    rather than checking the sign of remaining_amount directly.
    """

    id: UUID
    category_id: UUID
    category_name: str
    limit_amount: Decimal
    month: int
    year: int
    spent_amount: Decimal
    remaining_amount: Decimal
    percentage_used: Decimal
    is_exceeded: bool
    created_at: datetime

    @field_serializer("limit_amount", "spent_amount", "remaining_amount", "percentage_used")
    def serialise_decimal(self, value: Decimal) -> str:
        return str(value)

    @classmethod
    def from_domain(cls, summary: BudgetSummary) -> "BudgetResponse":
        return cls(
            id=summary.budget_id,
            category_id=summary.category_id,
            category_name=summary.category_name,
            limit_amount=summary.limit_amount,
            month=summary.month,
            year=summary.year,
            spent_amount=summary.spent_amount,
            remaining_amount=summary.remaining_amount,
            percentage_used=summary.percentage_used,
            is_exceeded=summary.is_exceeded,
            created_at=summary.created_at,
        )
