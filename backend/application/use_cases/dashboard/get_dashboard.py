"""
Get Dashboard Use Case
========================
Aggregates everything a personal-finance dashboard needs for one period
into a single call: income/expense totals, net savings, the top spending
categories, the most recent transactions, and total balance across all
accounts.

This use case exists specifically to keep the router thin. Without it,
the router would need to call four repository methods directly, do the
percentage arithmetic itself, and handle category-name lookups — that's
business logic, and business logic belongs in the application layer,
not in an HTTP handler.

Why a period (date_from/date_to) rather than "current month"?
    The router defaults to the current calendar month when the client
    doesn't specify one (see presentation/api/routers/dashboard.py), but
    the use case itself stays generic — "give me the dashboard for any
    date range" — so it can be reused for "this year", "last 90 days",
    or a custom range without any change here.

Why compute percentage_of_expenses here and not in TransactionRepository?
    CategoryTotal (the repository's return type) is a pure aggregation
    read-model — it has no concept of "percentage of what". Turning a raw
    total into a percentage of period spending is domain-adjacent
    arithmetic, which belongs at the use-case layer, consistent with how
    BudgetSummary.build() computes percentage_used from raw numbers.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.transaction import Transaction
from domain.repositories.account_repository import AccountRepository
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.transaction_repository import TransactionRepository


@dataclass
class GetDashboardInput:
    user_id: UUID
    date_from: date
    date_to: date
    top_categories_limit: int = 5
    recent_transactions_limit: int = 10


@dataclass
class CategoryBreakdown:
    """One row of the top-expense-categories breakdown."""

    category_id: UUID | None  # None = uncategorized
    category_name: str  # "Uncategorized" when category_id is None
    total_amount: Decimal
    percentage_of_expenses: Decimal  # 0.00 when there is no expense total to divide by


@dataclass
class DashboardSummary:
    date_from: date
    date_to: date
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal  # total_income - total_expense; can be negative
    total_balance: Decimal  # sum of current_balance across all of the user's accounts
    top_expense_categories: list[CategoryBreakdown]
    recent_transactions: list[Transaction]


class GetDashboard:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
        account_repository: AccountRepository,
    ) -> None:
        self._transaction_repo = transaction_repository
        self._category_repo = category_repository
        self._account_repo = account_repository

    def execute(self, input_data: GetDashboardInput) -> DashboardSummary:
        """
        Build the full dashboard summary for one user over one date range.

        No exceptions are raised for "no data" cases — an account with no
        transactions simply gets zeroed totals and empty lists. This use
        case never fails for a valid, authenticated user; there is no
        invalid state to guard against once user_id is trusted (which the
        router guarantees by always sourcing it from the authenticated User).
        """
        total_income = self._transaction_repo.get_period_income_total(
            user_id=input_data.user_id,
            date_from=input_data.date_from,
            date_to=input_data.date_to,
        )
        total_expense = self._transaction_repo.get_period_expense_total(
            user_id=input_data.user_id,
            date_from=input_data.date_from,
            date_to=input_data.date_to,
        )
        net_savings = total_income - total_expense

        raw_top_categories = self._transaction_repo.get_top_expense_categories(
            user_id=input_data.user_id,
            date_from=input_data.date_from,
            date_to=input_data.date_to,
            limit=input_data.top_categories_limit,
        )
        top_expense_categories = [
            self._to_breakdown(row, input_data.user_id, total_expense)
            for row in raw_top_categories
        ]

        recent_transactions = self._transaction_repo.list_recent(
            user_id=input_data.user_id,
            limit=input_data.recent_transactions_limit,
        )

        accounts = self._account_repo.list_by_user(input_data.user_id)
        total_balance = sum(
            (account.current_balance for account in accounts), start=Decimal("0")
        )

        return DashboardSummary(
            date_from=input_data.date_from,
            date_to=input_data.date_to,
            total_income=total_income,
            total_expense=total_expense,
            net_savings=net_savings,
            total_balance=total_balance,
            top_expense_categories=top_expense_categories,
            recent_transactions=recent_transactions,
        )

    def _to_breakdown(
        self,
        row,
        user_id: UUID,
        total_expense: Decimal,
    ) -> CategoryBreakdown:
        """
        Convert one raw CategoryTotal row into a CategoryBreakdown, resolving
        the human-readable category name and computing its share of period
        spending.

        row.category_id is None for uncategorized transactions — grouped
        together by the repository query, not per-transaction.
        """
        if row.category_id is not None:
            category = self._category_repo.get_by_id(row.category_id, user_id)
            category_name = category.name if category is not None else "(deleted category)"
        else:
            category_name = "Uncategorized"

        if total_expense == Decimal("0"):
            percentage = Decimal("0.00")
        else:
            percentage = (row.total_amount / total_expense * Decimal("100")).quantize(
                Decimal("0.01")
            )

        return CategoryBreakdown(
            category_id=row.category_id,
            category_name=category_name,
            total_amount=row.total_amount,
            percentage_of_expenses=percentage,
        )
