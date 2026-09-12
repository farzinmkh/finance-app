"""
Delete Account Use Case
=========================
Deletes an account belonging to the authenticated user.

Follows the exact same shape as DeleteCategory and DeleteBudget:
verify ownership, then delegate to the repository.

The repository (not this use case) is responsible for translating the
database's ON DELETE RESTRICT violation into a ConflictError when the
account still has transactions or transfers referencing it — that is a
persistence-layer concern, consistent with how SQLAlchemyCategoryRepository
translates a duplicate-name IntegrityError into ConflictError.
"""

from uuid import UUID

from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository


class DeleteAccount:
    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    def execute(self, account_id: UUID, user_id: UUID) -> None:
        """
        Delete an account.

        Raises:
            NotFoundError: if the account does not exist or belongs to
                           a different user.
            ConflictError: if the account still has transactions or
                           transfers referencing it (raised by the repository).
        """
        account = self._account_repository.get_by_id(account_id, user_id)
        if account is None:
            raise NotFoundError(f"Account with ID '{account_id}' was not found.")

        self._account_repository.delete(account_id, user_id)
