"""
Transfer Domain Entity
=======================
Represents the movement of money between two accounts owned by the same user.

Core invariants enforced by Transfer.create():
  1. from_account_id != to_account_id   — cannot transfer to yourself
  2. amount > 0 (Decimal)               — must be a positive exact value

What Transfer does NOT do:
  - Update account balances (the use case does this)
  - Create transaction legs (the use case does this)
  - Verify accounts exist or belong to the user (the use case does this)

The Transfer entity is a pure value object representing the financial intent.
The CreateTransfer use case coordinates all the side effects.

Why is UpdateTransfer not supported?
  Updating a transfer's amount requires:
    - Reversing the old balance effect on both accounts
    - Applying the new balance effect on both accounts
    - Updating both transaction legs
  This is equivalent to deleting and recreating the transfer.
  We make this explicit: users delete and recreate rather than edit.

Dependency rule: imports only stdlib and domain/exceptions.py.
"""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError


@dataclass
class Transfer:
    """
    A transfer of money between two accounts owned by the same user.

    The transfer owns exactly two Transaction records (its 'legs'):
      - An expense transaction on from_account  (money leaving)
      - An income  transaction on to_account    (money arriving)

    These legs are found by querying:
        SELECT * FROM transactions WHERE transfer_id = :this_transfer_id

    Do not construct this directly. Use Transfer.create().
    """

    id: UUID
    user_id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    date: date
    notes: str | None
    created_at: datetime

    # ── Factory method ──────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user_id: UUID,
        from_account_id: UUID,
        to_account_id: UUID,
        amount: Decimal,
        date: date,
        notes: str | None = None,
    ) -> "Transfer":
        """
        Create a new Transfer with validated fields.

        Does NOT persist anything. Does NOT update balances.
        The CreateTransfer use case calls this, then handles all side effects.

        Raises:
            DomainValidationError: if the accounts are the same, or if
                                   the amount is zero, negative, or not Decimal.
        """
        cls._validate_different_accounts(from_account_id, to_account_id)
        validated_amount = cls._validate_amount(amount)

        return cls(
            id=uuid4(),
            user_id=user_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=validated_amount,
            date=date,
            notes=notes,
            created_at=datetime.now(timezone.utc),
        )

    # ── Private validation ───────────────────────────────────────────────────

    @staticmethod
    def _validate_different_accounts(
        from_account_id: UUID, to_account_id: UUID
    ) -> None:
        """
        Enforce that source and destination are different accounts.

        Transferring from an account to itself would leave both balances
        unchanged while creating two transaction records — a meaningless
        and confusing operation.
        """
        if from_account_id == to_account_id:
            raise DomainValidationError(
                "Source and destination accounts must be different. "
                "A transfer from an account to itself has no financial effect."
            )

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """
        Amount must be a positive Decimal.

        We check the type explicitly because a float would pass comparison
        checks but introduce the floating-point precision errors that
        monetary calculations must avoid.
        """
        if not isinstance(amount, Decimal):
            raise DomainValidationError(
                f"Transfer amount must be a Decimal, not {type(amount).__name__}. "
                f"Never use float for monetary values."
            )
        if amount <= Decimal("0"):
            raise DomainValidationError(
                f"Transfer amount must be greater than zero (got {amount})."
            )
        return amount
