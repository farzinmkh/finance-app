"""
Create Account Use Case
========================
Handles the creation of a new financial account for a user.

Responsibility of this use case:
- Delegate construction and validation to Account.create()
- Persist the new account via the repository
- Return the created account

What this use case deliberately does NOT do:
- Validate field formats (Pydantic handles that at the API boundary)
- Know about HTTP, JSON, or SQLAlchemy
- Commit the database transaction (the session manager handles that)
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.entities.account import Account, AccountType
from domain.repositories.account_repository import AccountRepository


@dataclass
class CreateAccountInput:
    """
    The data required to create a new account.

    This is a plain dataclass — not a Pydantic model.
    It belongs to the application layer and is framework-agnostic.
    The API layer (Pydantic schema) is responsible for converting
    the incoming HTTP request into this input object.
    """

    user_id: UUID
    name: str
    account_type: AccountType
    currency: str
    opening_balance: Decimal


class CreateAccount:
    """
    Use case: create a new financial account.

    Receives an AccountRepository via constructor injection.
    The injected repository can be:
    - SQLAlchemyAccountRepository in production
    - FakeAccountRepository in unit tests

    This is how we achieve testability without a database.
    """

    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    def execute(self, input_data: CreateAccountInput) -> Account:
        """
        Create and persist a new account.

        Raises:
            DomainValidationError: if the name or currency is invalid
                                   (raised by Account.create()).
        """
        # Account.create() validates business rules and constructs the entity.
        # If validation fails, it raises DomainValidationError before the
        # repository is ever called — no partial state is persisted.
        account = Account.create(
            user_id=input_data.user_id,
            name=input_data.name,
            account_type=input_data.account_type,
            currency=input_data.currency,
            opening_balance=input_data.opening_balance,
        )

        return self._account_repository.save(account)
