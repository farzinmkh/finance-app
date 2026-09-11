"""
Transaction API Schemas
=========================
Request/response models for the transactions endpoints.

Notable design points:

1. amount is validated with gt=0 at the Pydantic layer (fast, cheap check),
   AND re-validated by Transaction._validate_amount() in the domain layer.
   Both layers matter: Pydantic catches malformed client input early;
   the domain layer guarantees the invariant no matter what caller invokes it.

2. UpdateTransactionRequest has an explicit `clear_category: bool = False`
   flag, mirroring UpdateTransactionInput.update_category. A plain
   `category_id: UUID | None` field cannot distinguish "leave unchanged"
   from "clear it" — both would arrive as null/absent over JSON. The
   flag makes "clear the category" an explicit, deliberate action.

3. TransactionResponse serialises Decimal as a string, exactly like
   AccountResponse and TransferResponse, to avoid IEEE-754 float rounding
   on the client.

4. TransactionsPageResponse mirrors the application-layer TransactionsPage
   dataclass (items, total, page, page_size, total_pages) so the router
   can build it with a single from_page() call.
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator

from application.use_cases.transactions.list_transactions import TransactionsPage
from domain.entities.transaction import Transaction, TransactionType


# ── Request schemas ───────────────────────────────────────────────────────────


class CreateTransactionRequest(BaseModel):
    account_id: UUID = Field(..., description="Account this transaction belongs to.")
    transaction_type: TransactionType = Field(..., description="'income' or 'expense'.")
    amount: Decimal = Field(..., gt=0, description="Transaction amount. Must be positive.")
    date: date_type = Field(..., description="Financial date of the transaction (YYYY-MM-DD).")
    category_id: UUID | None = Field(
        default=None, description="Optional category. Must match transaction_type."
    )
    notes: str | None = Field(default=None, max_length=500, description="Optional notes.")

    @field_validator("amount")
    @classmethod
    def amount_must_be_decimal_compatible(cls, v: Decimal) -> Decimal:
        """Ensure the amount has no more than 4 decimal places (matches NUMERIC(19,4))."""
        if v.as_tuple().exponent < -4:
            raise ValueError("Amount cannot have more than 4 decimal places.")
        return v


class UpdateTransactionRequest(BaseModel):
    """
    All fields optional — the client sends only what it wants to change.

    account_id is intentionally absent: moving a transaction between
    accounts is a delete + create, not an update (see update_transaction.py
    docstring in the application layer).
    """

    amount: Decimal | None = Field(default=None, gt=0, description="New amount, if changing.")
    transaction_type: TransactionType | None = Field(
        default=None, description="New type, if changing."
    )
    date: date_type | None = Field(default=None, description="New financial date, if changing.")
    notes: str | None = Field(default=None, max_length=500, description="New notes, if changing.")
    category_id: UUID | None = Field(
        default=None,
        description=(
            "New category id. Ignored unless provided alongside "
            "clear_category=true or a non-null value — see clear_category."
        ),
    )
    clear_category: bool = Field(
        default=False,
        description=(
            "Set true to explicitly remove the category (sets it to null). "
            "If false and category_id is provided, the category is changed "
            "to category_id. If false and category_id is omitted, the "
            "category is left unchanged."
        ),
    )

    @field_validator("amount")
    @classmethod
    def amount_must_be_decimal_compatible(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v.as_tuple().exponent < -4:
            raise ValueError("Amount cannot have more than 4 decimal places.")
        return v


# ── Response schemas ──────────────────────────────────────────────────────────


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    category_id: UUID | None
    transaction_type: TransactionType
    amount: Decimal
    date: date_type
    notes: str | None
    transfer_id: UUID | None
    created_at: datetime

    @field_serializer("amount")
    def serialise_decimal(self, value: Decimal) -> str:
        return str(value)

    @classmethod
    def from_domain(cls, transaction: Transaction) -> "TransactionResponse":
        return cls(
            id=transaction.id,
            account_id=transaction.account_id,
            category_id=transaction.category_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            date=transaction.date,
            notes=transaction.notes,
            transfer_id=transaction.transfer_id,
            created_at=transaction.created_at,
        )


class TransactionsPageResponse(BaseModel):
    """
    Paginated envelope for GET /transactions.

    Mirrors the application-layer TransactionsPage dataclass field-for-field
    so the router doesn't need to compute anything beyond mapping items.
    """

    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def from_page(cls, page: TransactionsPage) -> "TransactionsPageResponse":
        return cls(
            items=[TransactionResponse.from_domain(t) for t in page.items],
            total=page.total,
            page=page.page,
            page_size=page.page_size,
            total_pages=page.total_pages,
        )
