"""
List Accounts Use Case
=======================
Returns all accounts belonging to the authenticated user.

This use case is intentionally simple — it delegates entirely to the
repository. Its value is that it sits in the right layer (application),
keeping the route handler thin and making the operation independently
testable.
"""

from uuid import UUID

from domain.entities.account import Account
from domain.repositories.account_repository import AccountRepository


class ListAccounts:
    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    def execute(self, user_id: UUID) -> list[Account]:
        """
        Return all accounts for the user, ordered by creation date.

        Returns an empty list if the user has no accounts.
        Never raises an exception for an empty result.
        """
        return self._account_repository.list_by_user(user_id)
