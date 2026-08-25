"""Get Transaction Use Case"""
from uuid import UUID

from domain.entities.transaction import Transaction
from domain.exceptions import NotFoundError
from domain.repositories.transaction_repository import TransactionRepository


class GetTransaction:
    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self._repo = transaction_repository

    def execute(self, transaction_id: UUID, user_id: UUID) -> Transaction:
        transaction = self._repo.get_by_id(transaction_id, user_id)
        if transaction is None:
            raise NotFoundError(f"Transaction '{transaction_id}' was not found.")
        return transaction
