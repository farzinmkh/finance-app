"""Get Transfer Use Case"""
from uuid import UUID

from domain.entities.transfer import Transfer
from domain.exceptions import NotFoundError
from domain.repositories.transfer_repository import TransferRepository


class GetTransfer:
    def __init__(self, transfer_repository: TransferRepository) -> None:
        self._repo = transfer_repository

    def execute(self, transfer_id: UUID, user_id: UUID) -> Transfer:
        transfer = self._repo.get_by_id(transfer_id, user_id)
        if transfer is None:
            raise NotFoundError(f"Transfer '{transfer_id}' was not found.")
        return transfer
