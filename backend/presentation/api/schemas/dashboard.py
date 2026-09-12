"""
Dashboard API Schema
======================
Single response model for GET /dashboard.

Reuses TransactionResponse from the transactions schema for
recent_transactions rather than redefining a transaction shape here —
one canonical representation of "a transaction over the wire", used
everywhere a transaction appears in a response.
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_serializer

from application.use_cases.dashboard.get_dashboard import DashboardSummary
from presentation.api.schemas.transactions import TransactionResponse


class CategoryBreakdownResponse(BaseModel):
    category_id: UUID | None
    category_name: str
    total_amount: Decimal
    percentage_of_expenses: Decimal

    @field_serializer("total_amount", "percentage_of_expenses")
    def serialise_decimal(self, value: Decimal) -> str:
        return str(value)


class DashboardResponse(BaseModel):
    date_from: date
    date_to: date
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal
    total_balance: Decimal
    top_expense_categories: list[CategoryBreakdownResponse]
    recent_transactions: list[TransactionResponse]

    @field_serializer("total_income", "total_expense", "net_savings", "total_balance")
    def serialise_decimal(self, value: Decimal) -> str:
        return str(value)

    @classmethod
    def from_domain(cls, summary: DashboardSummary) -> "DashboardResponse":
        return cls(
            date_from=summary.date_from,
            date_to=summary.date_to,
            total_income=summary.total_income,
            total_expense=summary.total_expense,
            net_savings=summary.net_savings,
            total_balance=summary.total_balance,
            top_expense_categories=[
                CategoryBreakdownResponse(
                    category_id=c.category_id,
                    category_name=c.category_name,
                    total_amount=c.total_amount,
                    percentage_of_expenses=c.percentage_of_expenses,
                )
                for c in summary.top_expense_categories
            ],
            recent_transactions=[
                TransactionResponse.from_domain(t) for t in summary.recent_transactions
            ],
        )
