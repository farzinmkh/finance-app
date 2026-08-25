"""
Transfer Repository Interface
================================
Defines the contract for transfer data access.

Note on deletion responsibility:
  The delete() method here removes only the Transfer record.
  The DeleteTransfer USE CASE is responsible for deleting the transaction
  legs first (via TransactionRepository.delete_by_transfer_id), then
  calling this method.

  This ordering is mandatory due to the FK constraint:
      transactions.transfer_id → transfers.id (ON DELETE RESTRICT)
  Attempting to delete a Transfer while its legs exist raises a DB error.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.transfer import Transfer


class TransferRepository(ABC):

    @abstractmethod
    def get_by_id(self, transfer_id: UUID, user_id: UUID) -> Transfer | None:
        """
        Return the transfer if it exists and belongs to user_id.
        Return None otherwise (not found OR wrong user).
        """
        ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
    ) -> list[Transfer]:
        """
        Return all transfers for the user.

        account_id filter: if provided, returns transfers where either
        from_account_id OR to_account_id matches (money flowing either
        direction through the account).

        Ordered by date descending.
        """
        ...

    @abstractmethod
    def save(self, transfer: Transfer) -> Transfer:
        """
        Persist a new Transfer record. Does NOT commit.

        Must be called BEFORE saving the transaction legs, because the
        legs have a FK (transfer_id) that references this transfer's id.
        """
        ...

    @abstractmethod
    def delete(self, transfer_id: UUID, user_id: UUID) -> None:
        """
        Delete the Transfer record. Does NOT commit.

        PRECONDITION: the caller (DeleteTransfer use case) must have
        already deleted the transaction legs via
        TransactionRepository.delete_by_transfer_id(transfer_id).
        Failing to do so will raise an IntegrityError from the database.
        """
        ...
