"""List Transfers Use Case"""
from uuid import UUID

from domain.entities.transfer import Transfer
from domain.repositories.transfer_repository import TransferRepository


class ListTransfers:
    def __init__(self, transfer_repository: TransferRepository) -> None:
        self._repo = transfer_repository

    def execute(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
    ) -> list[Transfer]:
        """
        Return all transfers for the user.

        account_id: if provided, filters to transfers involving that
                    account (either as source or destination).
        """
        return self._repo.list_by_user(user_id, account_id)
