"""
Create Transaction Use Case
============================
Records a new income or expense transaction and atomically updates the
owning account's current balance.

This use case coordinates three repositories in a single operation:
  1. AccountRepository  — verify the account exists and update its balance
  2. CategoryRepository — verify the category (if provided) and type-check it
  3. TransactionRepository — persist the new transaction

All three happen within one database session (committed by get_db when
the route handler returns successfully). If any step fails, everything
rolls back — no partial state is ever saved.

Balance update:
  income  → account.current_balance += amount
  expense → account.current_balance -= amount
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.account import Account
from domain.entities.category import Category
from domain.entities.transaction import Transaction, TransactionType
from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.transaction_repository import TransactionRepository


@dataclass
class CreateTransactionInput:
    user_id: UUID
    account_id: UUID
    transaction_type: TransactionType
    amount: Decimal
    date: date
    category_id: UUID | None = None
    notes: str | None = None


class CreateTransaction:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._transaction_repo = transaction_repository
        self._account_repo = account_repository
        self._category_repo = category_repository

    def execute(self, input_data: CreateTransactionInput) -> Transaction:
        """
        Create a transaction and update the account balance atomically.

        Raises:
            NotFoundError: if the account or category does not exist, or
                           does not belong to the authenticated user.
            DomainValidationError: if the amount is invalid, or the
                                   category type does not match the
                                   transaction type.
        """
        # ── Step 1: Verify the account exists and belongs to this user ──────
        account = self._account_repo.get_by_id(input_data.account_id, input_data.user_id)
        if account is None:
            raise NotFoundError(
                f"Account '{input_data.account_id}' was not found."
            )

        # ── Step 2: Verify the category (if provided) ────────────────────────
        if input_data.category_id is not None:
            category = self._category_repo.get_by_id(
                input_data.category_id, input_data.user_id
            )
            if category is None:
                raise NotFoundError(
                    f"Category '{input_data.category_id}' was not found."
                )
            # Enforce: income transaction → income category only
            Transaction.validate_category_type_match(
                input_data.transaction_type, category.category_type
            )

        # ── Step 3: Create the transaction entity (validates amount) ─────────
        transaction = Transaction.create(
            account_id=input_data.account_id,
            user_id=input_data.user_id,
            transaction_type=input_data.transaction_type,
            amount=input_data.amount,
            date=input_data.date,
            category_id=input_data.category_id,
            notes=input_data.notes,
        )

        # ── Step 4: Update account balance ───────────────────────────────────
        # This is the critical invariant. The balance change and the transaction
        # insert are saved in the same database transaction (committed together).
        _apply_to_balance(account, transaction.transaction_type, transaction.amount)
        self._account_repo.update(account)

        # ── Step 5: Persist the transaction ──────────────────────────────────
        return self._transaction_repo.save(transaction)


def _apply_to_balance(
    account: Account,
    transaction_type: TransactionType,
    amount: Decimal,
) -> None:
    """
    Apply a transaction's effect to an account's current balance.

    income  → balance increases (money coming in)
    expense → balance decreases (money going out)

    This is a module-level helper (not a method on Account) so that it
    can be reused by CreateTransaction, UpdateTransaction, and DeleteTransaction
    without importing TransactionType into the Account entity.
    """
    if transaction_type == TransactionType.INCOME:
        account.current_balance += amount
    else:
        account.current_balance -= amount


def _reverse_from_balance(
    account: Account,
    transaction_type: TransactionType,
    amount: Decimal,
) -> None:
    """
    Reverse a transaction's effect from an account's current balance.

    This is the opposite of _apply_to_balance.
    Used when updating (reverse old, apply new) or deleting a transaction.
    """
    if transaction_type == TransactionType.INCOME:
        account.current_balance -= amount
    else:
        account.current_balance += amount
