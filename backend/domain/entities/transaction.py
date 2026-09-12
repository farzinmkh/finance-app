"""
Transaction Domain Entity
==========================
Represents a single financial event: money moving into or out of an account.

This is the most financially sensitive entity in the application.

Key design decisions:
---------------------
1. amount is ALWAYS positive (Decimal, > 0). Direction is encoded in
   transaction_type (income/expense), not in the sign of the amount.
   This makes balance calculations unambiguous and avoids sign errors.

2. date is datetime.date, not datetime.datetime. A transaction's
   financial date is a calendar day ("I paid rent on August 1st"), not
   a moment in time. The system timestamp (created_at) records when the
   record was entered — these are separate concepts.

3. transfer_id is set only for transactions that are legs of a Transfer.
   A transaction with a transfer_id CANNOT be independently edited or
   deleted — the TransactionLockedError enforces this in use cases.

4. category validation (type match) is a domain rule but requires knowing
   the category object. It is enforced in the use case via the static
   method validate_category_type_match(), keeping the rule in the domain
   layer without requiring the entity to fetch the category.

Dependency rule: imports only stdlib and domain exceptions.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError
from domain.entities.category import CategoryType


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Transaction:
    """
    A single income or expense event against one Account.

    Do not construct this directly. Use Transaction.create().
    """

    id: UUID
    account_id: UUID
    user_id: UUID
    category_id: UUID | None  # optional — transactions can be uncategorised
    transaction_type: TransactionType
    amount: Decimal            # always positive; direction is in transaction_type
    date: date                 # financial date (e.g. 2024-08-01)
    notes: str | None          # optional free-text description
    transfer_id: UUID | None   # set only when this is a leg of a Transfer
    created_at: datetime

    # ── Factory method ──────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        account_id: UUID,
        user_id: UUID,
        transaction_type: TransactionType,
        amount: Decimal,
        date: date,
        category_id: UUID | None = None,
        notes: str | None = None,
        transfer_id: UUID | None = None,
    ) -> "Transaction":
        """
        Create a new Transaction with validated fields.

        Note: category type matching (income category ↔ income transaction)
        is validated in the use case via validate_category_type_match(),
        because the entity does not have access to the Category object.

        Raises:
            DomainValidationError: if the amount is zero or negative.
        """
        validated_amount = cls._validate_amount(amount)

        return cls(
            id=uuid4(),
            account_id=account_id,
            user_id=user_id,
            category_id=category_id,
            transaction_type=transaction_type,
            amount=validated_amount,
            date=date,
            notes=notes,
            transfer_id=transfer_id,
            created_at=datetime.now(timezone.utc),
        )

    # ── Domain rules ─────────────────────────────────────────────────────────

    @staticmethod
    def validate_category_type_match(
        transaction_type: TransactionType,
        category_type: CategoryType,
    ) -> None:
        """
        Enforce that a category's type matches the transaction's type.

        This is a domain rule: you cannot assign an expense category to
        an income transaction, or vice versa. Doing so would make category
        reporting misleading and budgets untrustworthy.

        Called from use cases (CreateTransaction, UpdateTransaction) where
        both the transaction type and the category object are available.

        Raises:
            DomainValidationError: if the types do not match.
        """
        if transaction_type.value != category_type.value:
            raise DomainValidationError(
                f"Cannot assign a '{category_type.value}' category to an "
                f"'{transaction_type.value}' transaction. "
                f"The category type must match the transaction type."
            )

    # ── Private validation ───────────────────────────────────────────────────

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """
        Amount must be a positive Decimal (strictly greater than zero).

        Zero is rejected because a zero-amount transaction has no financial
        meaning and is almost certainly a data-entry mistake.

        Negative amounts are rejected because direction is encoded in
        transaction_type, not the sign of the amount.
        """
        if not isinstance(amount, Decimal):
            raise DomainValidationError(
                f"Amount must be a Decimal, not {type(amount).__name__}. "
                f"Never use float for monetary values."
            )
        if amount <= Decimal("0"):
            raise DomainValidationError(
                f"Transaction amount must be greater than zero (got {amount})."
            )
        return amount
