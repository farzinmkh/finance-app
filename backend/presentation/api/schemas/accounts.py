"""
Account API Schemas
====================
Pydantic models for validating incoming requests and serialising responses.

Two clear categories:
    Request schemas  — validate and parse data coming IN from the client.
    Response schemas — define exactly what data goes OUT to the client.

Why are these separate from domain entities?
--------------------------------------------
The API contract and the domain model often differ legitimately:
- Response schemas may omit internal fields (no hashed_password ever)
- Response schemas may rename or reshape fields for the API consumer
- Request schemas may accept formats the domain entity doesn't use

Decimal serialisation:
-----------------------
Monetary values are serialised as strings in JSON responses.

Why strings and not numbers?
    JSON numbers are IEEE 754 floats. A JavaScript client reading the JSON
    would convert "1234.56" to a float, potentially introducing rounding errors.
    Returning "1234.5600" as a string guarantees the client receives the exact
    value and can parse it with whatever precision library it chooses.

    The @field_serializer decorator tells Pydantic to apply this conversion
    when building the JSON response.

Input validation strategy:
    Pydantic validates structure (type, presence, basic format).
    Domain entities validate business rules (name not empty, currency 3 chars).
    Both layers are needed — they catch different classes of error.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator

from domain.entities.account import Account, AccountType


# ── Request schemas (incoming data from the client) ──────────────────────────


class CreateAccountRequest(BaseModel):
    """
    Payload for POST /accounts.

    Pydantic validates types here. Business rules (name not empty,
    currency exactly 3 chars) are validated by Account.create() in the domain.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for the account (e.g. 'HSBC Checking').",
    )
    account_type: AccountType = Field(
        ...,
        description="Type of account: checking, savings, credit, or cash.",
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g. EUR, USD, GBP).",
    )
    opening_balance: Decimal = Field(
        default=Decimal("0"),
        description=(
            "Starting balance. Use a positive value for an account with funds, "
            "a negative value for a credit account you already owe on, "
            "or 0 for a brand new account."
        ),
    )

    @field_validator("currency")
    @classmethod
    def currency_must_be_alphabetic(cls, v: str) -> str:
        """Ensure currency contains only letters (catches '1US', 'E R', etc.)."""
        if not v.strip().isalpha():
            raise ValueError("Currency code must contain only letters (e.g. EUR, USD).")
        return v.upper()


class UpdateAccountRequest(BaseModel):
    """
    Payload for PATCH /accounts/{account_id}.

    All fields are optional — the client sends only what they want to change.
    At least one field should be provided (enforced below).
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New display name.",
    )
    account_type: AccountType | None = Field(
        default=None,
        description="New account type.",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Name must not be empty or contain only whitespace.")
        return v


# ── Response schema (outgoing data to the client) ────────────────────────────


class AccountResponse(BaseModel):
    """
    The account representation returned by the API.

    All fields are explicitly declared. No extra fields from the domain entity
    or ORM model can accidentally leak into responses.

    Monetary fields (opening_balance, current_balance) are serialised
    as strings to preserve decimal precision in JSON.
    """

    id: UUID
    name: str
    account_type: AccountType
    currency: str
    opening_balance: Decimal
    current_balance: Decimal
    created_at: datetime

    @field_serializer("opening_balance", "current_balance")
    def serialise_decimal(self, value: Decimal) -> str:
        """
        Serialise Decimal as a string in JSON responses.

        str(Decimal("1234.5600")) → "1234.5600"

        This preserves all significant figures and prevents any floating-point
        conversion from occurring between our server and the client.
        """
        return str(value)

    @classmethod
    def from_domain(cls, account: Account) -> "AccountResponse":
        """
        Construct a response schema from a domain entity.

        Having a named factory method makes the intent clear and
        keeps the mapping in one place.
        """
        return cls(
            id=account.id,
            name=account.name,
            account_type=account.account_type,
            currency=account.currency,
            opening_balance=account.opening_balance,
            current_balance=account.current_balance,
            created_at=account.created_at,
        )
