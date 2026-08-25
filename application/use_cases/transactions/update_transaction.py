"""
Update Transaction Use Case
============================
Updates a transaction's fields and atomically adjusts the account balance.

Balance recalculation is the core complexity here.
When an amount or type changes, we must reverse the OLD effect and apply
the NEW effect — not just replace the old amount with the new one.

Example:
  Before: income $100  → account balance was +$100 from this transaction
  Change to: income $150
  Naive:  balance += $150   → WRONG (balance becomes +$250 from this tx)
  Correct: reverse old (+$100 → -$100), apply new (-$100 + $150 = +$150) ✓

The formula for any combination of type/amount change:
  balance_delta = new_effect - old_effect
  where:
    effect of income  transaction = +amount
    effect of expense transaction = -amount

What CAN be updated:
  amount          → adjusts account balance atomically
  transaction_type → adjusts account balance atomically
  category_id     → no balance effect; validates type match if provided
  date            → no balance effect; pure metadata
  notes           → no balance effect; pure metadata

What CANNOT be updated:
  account_id → changing which account holds a transaction would require
               debiting one account and crediting another — that is a
               delete + create, not an update.

Locked transactions (transfer_id IS NOT NULL) cannot be independently
edited. The whole transfer must be deleted and recreated.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.transaction import Transaction, TransactionType
from domain.exceptions import NotFoundError, TransactionLockedError
from domain.repositories.account_repository import AccountRepository
from domain.repositories.category_repository import CategoryRepository
from domain.repositories.transaction_repository import TransactionRepository


@dataclass
class UpdateTransactionInput:
    transaction_id: UUID
    user_id: UUID
    # All optional — only provided fields are changed.
    # None means "leave this field unchanged" for most fields.
    amount: Decimal | None = None
    transaction_type: TransactionType | None = None
    date: date | None = None
    notes: str | None = None
    # Category update uses a flag because None is ambiguous:
    #   category_id=None could mean "don't touch category" OR "clear it".
    # Setting update_category=True explicitly means "apply new_category_id,
    # even if it is None (which clears the category)".
    update_category: bool = False
    new_category_id: UUID | None = None


class UpdateTransaction:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self._transaction_repo = transaction_repository
        self._account_repo = account_repository
        self._category_repo = category_repository

    def execute(self, input_data: UpdateTransactionInput) -> Transaction:
        """
        Apply the requested changes and correct the account balance if needed.

        Raises:
            NotFoundError: transaction or account not found / wrong user.
            TransactionLockedError: transaction is a transfer leg.
            DomainValidationError: new amount invalid or category type mismatch.
        """
        # ── Get the existing transaction ──────────────────────────────────────
        transaction = self._transaction_repo.get_by_id(
            input_data.transaction_id, input_data.user_id
        )
        if transaction is None:
            raise NotFoundError(
                f"Transaction '{input_data.transaction_id}' was not found."
            )

        # ── Block edits to transfer legs ──────────────────────────────────────
        if transaction.transfer_id is not None:
            raise TransactionLockedError(
                "This transaction is part of a transfer and cannot be edited "
                "independently. Delete and recreate the transfer to change its amount."
            )

        # ── Capture old values for balance recalculation ──────────────────────
        old_type = transaction.transaction_type
        old_amount = transaction.amount

        # ── Determine new values ───────────────────────────────────────────────
        new_type = input_data.transaction_type if input_data.transaction_type is not None else old_type
        new_amount = input_data.amount if input_data.amount is not None else old_amount

        # Validate new amount if changed
        if input_data.amount is not None:
            Transaction._validate_amount(input_data.amount)

        # ── Validate category type match ──────────────────────────────────────
        #
        # Two distinct scenarios must both be checked:
        #
        # A) Category is CHANGING (update_category=True, new_category_id set):
        #    Validate the NEW category against the NEW transaction type.
        #
        # B) Transaction type is CHANGING but category is NOT changing:
        #    The existing category must still match the NEW type.
        #    Example: expense→income while keeping an expense category → REJECT.
        #    Without this check, the category invariant could be silently broken.

        if input_data.update_category:
            # Scenario A: category is being changed
            if input_data.new_category_id is not None:
                category = self._category_repo.get_by_id(
                    input_data.new_category_id, input_data.user_id
                )
                if category is None:
                    raise NotFoundError(
                        f"Category '{input_data.new_category_id}' was not found."
                    )
                Transaction.validate_category_type_match(new_type, category.category_type)
            # If new_category_id is None (clearing the category), no type check needed.

        elif input_data.transaction_type is not None and transaction.category_id is not None:
            # Scenario B: type is changing but category is staying the same.
            # Re-validate the existing category against the new transaction type.
            existing_category = self._category_repo.get_by_id(
                transaction.category_id, input_data.user_id
            )
            if existing_category is not None:
                Transaction.validate_category_type_match(
                    new_type, existing_category.category_type
                )

        # ── Recalculate account balance if type or amount changed ─────────────
        balance_changed = (new_type != old_type) or (new_amount != old_amount)
        if balance_changed:
            account = self._account_repo.get_by_id(
                transaction.account_id, input_data.user_id
            )
            if account is None:
                raise NotFoundError(
                    f"Account '{transaction.account_id}' was not found."
                )

            # Reverse the old effect, apply the new effect.
            # income  effect = +amount  (positive contribution to balance)
            # expense effect = -amount  (negative contribution to balance)
            old_effect = old_amount if old_type == TransactionType.INCOME else -old_amount
            new_effect = new_amount if new_type == TransactionType.INCOME else -new_amount
            account.current_balance += (new_effect - old_effect)

            self._account_repo.update(account)

        # ── Apply field updates ────────────────────────────────────────────────
        if input_data.amount is not None:
            transaction.amount = input_data.amount
        if input_data.transaction_type is not None:
            transaction.transaction_type = input_data.transaction_type
        if input_data.date is not None:
            transaction.date = input_data.date
        if input_data.notes is not None:
            transaction.notes = input_data.notes
        if input_data.update_category:
            transaction.category_id = input_data.new_category_id

        return self._transaction_repo.update(transaction)
