"""
Update Account Use Case
========================
Updates the mutable fields of an existing account.

What CAN be updated:
    name         — The display name. Uses Account.update_name() which
                   re-applies the same validation rules as Account.create().
    account_type — The account type label. No business rules beyond the enum.

What CANNOT be updated (and why):
    currency       — Changing currency would require re-expressing all
                     historical transaction amounts in the new currency.
                     This is a complex financial operation beyond MVP scope.

    opening_balance — The opening balance is part of the balance invariant:
                      current_balance = opening_balance + Σ income - Σ expenses.
                      Changing it would silently shift the current balance,
                      which violates the integrity of the financial record.

    current_balance — Never set directly. Always maintained atomically
                      as a side effect of transaction operations.
"""

from dataclasses import dataclass
from uuid import UUID

from domain.entities.account import Account, AccountType
from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository


@dataclass
class UpdateAccountInput:
    """
    The data for an account update. All fields except account_id and
    user_id are optional — the caller supplies only what they want to change.
    """

    account_id: UUID
    user_id: UUID
    name: str | None = None
    account_type: AccountType | None = None


class UpdateAccount:
    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    def execute(self, input_data: UpdateAccountInput) -> Account:
        """
        Apply the requested changes to an existing account.

        Raises:
            NotFoundError: if the account does not exist or belongs to
                           a different user.
            DomainValidationError: if the new name is invalid
                                   (raised by Account.update_name()).
        """
        account = self._account_repository.get_by_id(
            input_data.account_id, input_data.user_id
        )

        if account is None:
            raise NotFoundError(
                f"Account with ID '{input_data.account_id}' was not found."
            )

        # Apply only the fields that were provided.
        # If a field is None, leave the existing value unchanged.
        if input_data.name is not None:
            # update_name() validates the new name using Account's own rules.
            # This keeps the validation logic in one place — the domain entity.
            account.update_name(input_data.name)

        if input_data.account_type is not None:
            account.account_type = input_data.account_type

        return self._account_repository.update(account)
