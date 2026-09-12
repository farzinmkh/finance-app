"""Transfer API Schemas"""
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator

from domain.entities.transfer import Transfer


class CreateTransferRequest(BaseModel):
    from_account_id: UUID = Field(..., description="Source account UUID.")
    to_account_id: UUID = Field(..., description="Destination account UUID.")
    amount: Decimal = Field(..., gt=0, description="Transfer amount. Must be positive.")
    date: date_type = Field(..., description="Financial date of the transfer (YYYY-MM-DD).")
    notes: str | None = Field(default=None, max_length=500, description="Optional notes.")

    @field_validator("amount")
    @classmethod
    def amount_must_be_decimal_compatible(cls, v: Decimal) -> Decimal:
        """Ensure the amount has no more than 4 decimal places."""
        if v.as_tuple().exponent < -4:
            raise ValueError("Amount cannot have more than 4 decimal places.")
        return v


class TransferResponse(BaseModel):
    id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    date: date_type
    notes: str | None
    created_at: datetime

    @field_serializer("amount")
    def serialise_decimal(self, value: Decimal) -> str:
        return str(value)

    @classmethod
    def from_domain(cls, transfer: Transfer) -> "TransferResponse":
        return cls(
            id=transfer.id,
            from_account_id=transfer.from_account_id,
            to_account_id=transfer.to_account_id,
            amount=transfer.amount,
            date=transfer.date,
            notes=transfer.notes,
            created_at=transfer.created_at,
        )
