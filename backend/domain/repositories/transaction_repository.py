"""
Transaction Repository Interface
==================================
Defines the contract for all transaction data access, including the
aggregation queries needed by the dashboard.

CategoryTotal is defined here (not in the domain entity) because it is
a read-model value type that only exists to support repository output.
It carries aggregated data, not business rules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class CategoryTotal:
    """
    The total spending for one category over a period.

    Returned by get_top_expense_categories(). The use case is responsible
    for looking up the human-readable category name from CategoryRepository
    using category_id (or marking it as 'Uncategorized' if category_id is None).
    """
    category_id: UUID | None   # None = uncategorized transactions
    total_amount: Decimal


class TransactionRepository(ABC):

    @abstractmethod
    def get_by_id(self, transaction_id: UUID, user_id: UUID) -> Transaction | None:
        """
        Return the transaction if it exists and belongs to user_id.
        Return None otherwise (not found OR wrong user — deliberate).
        """
        ...

    @abstractmethod
    def list_by_filters(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
        transaction_type: TransactionType | None = None,
        category_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Transaction]:
        """
        Return transactions matching all provided filters (AND logic).
        Ordered by date descending, then created_at descending.

        limit/offset support pagination for the API layer. limit=None
        (the default) returns all matching rows, preserving the original
        behaviour for any caller that does not need pagination.
        """
        ...

    @abstractmethod
    def count_by_filters(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
        transaction_type: TransactionType | None = None,
        category_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        """
        Return the total count of transactions matching the same filters as
        list_by_filters (ignoring limit/offset). Used by the API layer to
        compute total_pages for a paginated response.
        """
        ...

    @abstractmethod
    def list_recent(self, user_id: UUID, limit: int = 10) -> list[Transaction]:
        """
        Return the most recent transactions for a user.

        Includes transfer legs (unlike the income/expense totals which exclude them).
        Ordered by date descending, then created_at descending.
        """
        ...

    # ── Dashboard aggregation queries ─────────────────────────────────────────

    @abstractmethod
    def get_period_income_total(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        """
        Sum of income transaction amounts for the period.

        CRITICAL: Transfer legs (transfer_id IS NOT NULL) are EXCLUDED.
        A transfer from Account A to Account B creates an income transaction
        on Account B. Counting it as income would misrepresent the user's
        actual earnings — money moved between your own accounts is not income.

        Returns Decimal("0") if there are no qualifying transactions.
        Never returns None.
        """
        ...

    @abstractmethod
    def get_period_expense_total(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        """
        Sum of expense transaction amounts for the period.

        Transfer legs (transfer_id IS NOT NULL) are EXCLUDED for the same
        reason as get_period_income_total.

        Returns Decimal("0") if there are no qualifying transactions.
        Never returns None.
        """
        ...

    @abstractmethod
    def get_top_expense_categories(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
        limit: int = 5,
    ) -> list[CategoryTotal]:
        """
        Return the top spending categories by total amount, descending.

        - Only expense transactions counted.
        - Transfer legs (transfer_id IS NOT NULL) excluded.
        - Uncategorized transactions appear as CategoryTotal(category_id=None, ...).
        - Returns at most `limit` entries.
        - Returns [] if no qualifying transactions exist.

        The use case is responsible for looking up category names.
        """
        ...

    # ── Write operations ──────────────────────────────────────────────────────

    @abstractmethod
    def save(self, transaction: Transaction) -> Transaction:
        """Persist a new transaction. Does NOT commit."""
        ...

    @abstractmethod
    def update(self, transaction: Transaction) -> Transaction:
        """Persist changes to an existing transaction. Does NOT commit."""
        ...

    @abstractmethod
    def delete(self, transaction_id: UUID, user_id: UUID) -> None:
        """Delete a transaction by ID. Does NOT commit."""
        ...

    @abstractmethod
    def delete_by_transfer_id(self, transfer_id: UUID) -> None:
        """
        Delete all transaction legs belonging to a transfer.

        Called by DeleteTransfer BEFORE deleting the Transfer row itself,
        because transactions.transfer_id has ON DELETE RESTRICT.
        """
        ...

    @abstractmethod
    def get_category_month_spending(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Decimal:
        """
        Total expense spending for one category in one calendar month.

        This is the single authoritative source for budget spending calculations.
        All budget use cases call this method — the calculation is never
        duplicated in the entity, the API layer, or anywhere else.

        Rules (identical to period totals on the dashboard):
          - Only expense transactions counted (not income).
          - Transfer legs (transfer_id IS NOT NULL) are excluded.
          - Inclusive date range: first day of month through last day of month.
          - Returns Decimal("0") when no qualifying transactions exist.
          - Never returns None.

        The date range is computed from month/year using calendar.monthrange
        so February, 30-day months, and leap years are all handled correctly.
        """
        ...
