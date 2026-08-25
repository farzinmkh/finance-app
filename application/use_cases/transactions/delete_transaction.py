"""
Delete Transaction Use Case
============================
Removes a transaction and atomically reverses its effect on the account balance.

Reversal logic:
  income  was +amount → reverse by -amount
  expense was -amount → reverse by +amount

Locked transactions (part of a transfer) cannot be independently deleted.
Use DeleteTransfer to remove a transfer and both its legs together.
"""

from uuid import UUID

from domain.entities.transaction import TransactionType
from domain.exceptions import NotFoundError, TransactionLockedError
from domain.repositories.account_repository import AccountRepository
from domain.repositories.transaction_repository import TransactionRepository


class DeleteTransaction:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ) -> None:
        self._transaction_repo = transaction_repository
        self._account_repo = account_repository

    def execute(self, transaction_id: UUID, user_id: UUID) -> None:
        """
        Delete a transaction and reverse its balance effect.

        Raises:
            NotFoundError: transaction not found or belongs to different user.
            TransactionLockedError: transaction is a leg of a transfer.
        """
        transaction = self._transaction_repo.get_by_id(transaction_id, user_id)
        if transaction is None:
            raise NotFoundError(f"Transaction '{transaction_id}' was not found.")

        if transaction.transfer_id is not None:
            raise TransactionLockedError(
                "This transaction is part of a transfer and cannot be deleted "
                "independently. Use the transfer delete endpoint instead."
            )

        account = self._account_repo.get_by_id(transaction.account_id, user_id)
        if account is None:
            raise NotFoundError(
                f"Account '{transaction.account_id}' was not found."
            )

        # Reverse the transaction's effect on the balance.
        if transaction.transaction_type == TransactionType.INCOME:
            account.current_balance -= transaction.amount
        else:
            account.current_balance += transaction.amount

        self._account_repo.update(account)
        self._transaction_repo.delete(transaction_id, user_id)
