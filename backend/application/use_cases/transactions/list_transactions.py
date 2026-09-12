"""List Transactions Use Case"""
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.entities.transaction import Transaction, TransactionType
from domain.repositories.transaction_repository import TransactionRepository


@dataclass
class ListTransactionsFilters:
    user_id: UUID
    account_id: UUID | None = None
    transaction_type: TransactionType | None = None
    category_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    # Pagination — 1-indexed page number and page size.
    page: int = 1
    page_size: int = 20


@dataclass
class TransactionsPage:
    """
    A paginated slice of transactions plus the metadata needed to render
    pagination controls.

    Application-layer output type (like BudgetSummary) — not a domain
    entity, because pagination is a read-model/API concern, not a
    business rule.
    """

    items: list[Transaction]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        # Ceiling division without importing math.
        return (self.total + self.page_size - 1) // self.page_size


class ListTransactions:
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self._repo = transaction_repository

    def execute(self, filters: ListTransactionsFilters) -> TransactionsPage:
        page = max(filters.page, 1)
        page_size = max(filters.page_size, 1)
        offset = (page - 1) * page_size

        items = self._repo.list_by_filters(
            user_id=filters.user_id,
            account_id=filters.account_id,
            transaction_type=filters.transaction_type,
            category_id=filters.category_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
            limit=page_size,
            offset=offset,
        )
        total = self._repo.count_by_filters(
            user_id=filters.user_id,
            account_id=filters.account_id,
            transaction_type=filters.transaction_type,
            category_id=filters.category_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )

        return TransactionsPage(items=items, total=total, page=page, page_size=page_size)
