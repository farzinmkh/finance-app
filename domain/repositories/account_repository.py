"""
Account Repository Interface
=============================
Defines the contract for account data access.

Why define this in the domain layer?
--------------------------------------
This is the Dependency Inversion Principle (the 'D' in SOLID).

Without it:
    Use cases → SQLAlchemy repositories (use cases depend on infrastructure)
    Problem: you cannot test use cases without a database.

With it:
    Use cases → AccountRepository interface (depends on domain abstraction)
    Infrastructure → AccountRepository interface (implements the abstraction)
    Result: use cases can be tested with a simple in-memory fake.

This file has NO database-specific code. It does not know if the
data lives in SQLite, PostgreSQL, or a dictionary in memory.

The concrete implementation lives in:
    infrastructure/database/repositories/sqlalchemy_account_repository.py

The fake implementation for tests lives in:
    tests/unit/use_cases/fakes/fake_account_repository.py
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.account import Account


class AccountRepository(ABC):
    """
    Abstract interface for account persistence operations.

    Every method that retrieves account data requires BOTH account_id
    AND user_id. This is intentional — the user_id is the authorization
    gate. A repository implementation must never return an account that
    does not belong to the requesting user.
    """

    @abstractmethod
    def get_by_id(self, account_id: UUID, user_id: UUID) -> Account | None:
        """
        Retrieve an account by its ID, but only if it belongs to user_id.

        Returns None if the account does not exist OR belongs to a different user.
        The caller cannot distinguish between "not found" and "not yours" —
        both result in None. This prevents information leakage about whether
        an account ID exists at all.
        """
        ...

    @abstractmethod
    def list_by_user(self, user_id: UUID) -> list[Account]:
        """
        Retrieve all accounts owned by the given user, ordered by creation date.

        Returns an empty list if the user has no accounts.
        Never raises an exception for an empty result.
        """
        ...

    @abstractmethod
    def save(self, account: Account) -> Account:
        """
        Persist a new account to the data store.

        The account must have been created via Account.create(), which
        assigns its ID. The repository saves it and returns it.

        This method does NOT commit the database transaction.
        Committing is the responsibility of the session manager (get_db).
        This allows multiple operations to be grouped into one atomic commit.
        """
        ...

    @abstractmethod
    def update(self, account: Account) -> Account:
        """
        Persist changes to an existing account.

        The account must already exist. Raises NotFoundError if not found.

        This method does NOT commit the database transaction.
        """
        ...
