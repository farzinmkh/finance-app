"""
Account Domain Entity
======================
Represents a financial account owned by a user.

Examples: checking account, savings account, credit card, cash wallet.

Key design decisions:
---------------------
1. AccountType is a Python Enum so invalid types are caught at the type level,
   not just at runtime. AccountType("invalid") raises a ValueError immediately.

2. Account.create() is a classmethod factory. All validation of business rules
   happens here, before the object is constructed. You cannot create an Account
   with invalid data — the factory raises DomainValidationError.

3. Amounts use Python's decimal.Decimal. Never float. See the exceptions module
   for why this matters for financial correctness.

4. current_balance starts equal to opening_balance. It is then maintained
   automatically by the application every time a transaction is created,
   updated, or deleted. It is NEVER set directly by the user.

5. update_name() encapsulates the name-change business rules on the entity
   itself. This prevents duplicate validation logic from appearing in both
   the create() path and the update path.

Dependency rule: This file imports NOTHING outside the standard library
and domain/exceptions.py.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError


class AccountType(str, Enum):
    """
    The type of financial account.

    Inheriting from str makes this enum JSON-serialisable and lets FastAPI
    and Pydantic use the string values directly in API schemas.

    Values match the database CHECK constraint defined in the ORM model.
    """

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT = "credit"
    CASH = "cash"


@dataclass
class Account:
    """
    A financial account belonging to a user.

    Do not construct this directly. Use Account.create() to ensure
    business rules are validated before the object is built.
    """

    id: UUID
    user_id: UUID
    name: str
    account_type: AccountType
    currency: str
    opening_balance: Decimal
    current_balance: Decimal
    created_at: datetime

    # ── Factory method ──────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        account_type: AccountType,
        currency: str,
        opening_balance: Decimal,
    ) -> "Account":
        """
        Create a new Account with validated fields.

        This is the only correct way to construct an Account. It validates
        all business rules and sets fields that the user does not control
        (id, current_balance, created_at).

        Raises:
            DomainValidationError: if any business rule is violated.
        """
        validated_name = cls._validate_name(name)
        validated_currency = cls._validate_currency(currency)

        return cls(
            id=uuid4(),
            user_id=user_id,
            name=validated_name,
            account_type=account_type,
            currency=validated_currency,
            opening_balance=opening_balance,
            # current_balance starts equal to opening_balance.
            # The application maintains this field atomically as
            # transactions are created, updated, and deleted.
            current_balance=opening_balance,
            created_at=datetime.now(timezone.utc),
        )

    # ── Mutation methods ─────────────────────────────────────────────────────

    def update_name(self, new_name: str) -> None:
        """
        Update the account's display name.

        Applies the same validation rules as the factory method.
        Placing validation here (rather than in the use case) ensures
        that the Account entity enforces its own invariants, regardless
        of how the update is triggered.

        Raises:
            DomainValidationError: if the new name is invalid.
        """
        self.name = self._validate_name(new_name)

    # ── Private validation helpers ───────────────────────────────────────────

    @staticmethod
    def _validate_name(name: str) -> str:
        """
        Validate and normalise an account name.

        Returns the stripped name if valid.
        Raises DomainValidationError if invalid.
        """
        stripped = name.strip()
        if not stripped:
            raise DomainValidationError(
                "Account name must not be empty or contain only whitespace."
            )
        if len(stripped) > 100:
            raise DomainValidationError(
                f"Account name must not exceed 100 characters "
                f"(got {len(stripped)})."
            )
        return stripped

    @staticmethod
    def _validate_currency(currency: str) -> str:
        """
        Validate and normalise a currency code.

        Returns the uppercased currency code if valid.
        Raises DomainValidationError if not exactly 3 characters.

        Note: We validate length and normalise to uppercase here.
        We do not validate against a full list of ISO 4217 codes —
        that would require maintaining or fetching an external list.
        Length validation catches obvious mistakes (e.g. "EU", "EURO").
        """
        normalised = currency.strip().upper()
        if len(normalised) != 3:
            raise DomainValidationError(
                f"Currency must be a 3-letter ISO 4217 code (e.g. EUR, USD, GBP). "
                f"Got: '{currency}'."
            )
        return normalised
