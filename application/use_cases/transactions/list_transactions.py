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


class ListTransactions:
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self._repo = transaction_repository

    def execute(self, filters: ListTransactionsFilters) -> list[Transaction]:
        return self._repo.list_by_filters(
            user_id=filters.user_id,
            account_id=filters.account_id,
            transaction_type=filters.transaction_type,
            category_id=filters.category_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
