"""
Get Account Use Case
=====================
Retrieves a single account by ID for the authenticated user.

Authorization note:
    The repository's get_by_id() returns None for both "not found" and
    "belongs to a different user". The use case raises NotFoundError in
    both cases. This is intentional — we do not reveal to a user whether
    an account ID they do not own actually exists.
"""

from uuid import UUID

from domain.entities.account import Account
from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository


class GetAccount:
    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    def execute(self, account_id: UUID, user_id: UUID) -> Account:
        """
        Retrieve an account, enforcing that it belongs to the requesting user.

        Raises:
            NotFoundError: if the account does not exist or belongs to
                           a different user.
        """
        account = self._account_repository.get_by_id(account_id, user_id)

        if account is None:
            raise NotFoundError(
                f"Account with ID '{account_id}' was not found."
            )

        return account
