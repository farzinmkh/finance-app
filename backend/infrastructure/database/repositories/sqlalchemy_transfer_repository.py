"""
SQLAlchemy Transfer Repository
================================
Concrete implementation of TransferRepository.

Critical FK ordering note:
  TransactionModel has FK: transfer_id → transfers.id (RESTRICT)
  This means the Transfer row must exist BEFORE transaction legs are inserted,
  and legs must be deleted BEFORE the Transfer row is deleted.

  The USE CASE manages this ordering — not this repository.
  This repository's delete() method deletes ONLY the Transfer row.
  The use case calls TransactionRepository.delete_by_transfer_id() first.
"""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from domain.entities.transfer import Transfer
from domain.exceptions import NotFoundError
from domain.repositories.transfer_repository import TransferRepository
from infrastructure.database.models import TransferModel


class SQLAlchemyTransferRepository(TransferRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, transfer_id: UUID, user_id: UUID) -> Transfer | None:
        model = self._session.get(TransferModel, str(transfer_id))
        if model is None or model.user_id != str(user_id):
            return None
        return self._to_domain(model)

    def list_by_user(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
    ) -> list[Transfer]:
        stmt = (
            select(TransferModel)
            .where(TransferModel.user_id == str(user_id))
            .order_by(TransferModel.date.desc(), TransferModel.created_at.desc())
        )
        if account_id is not None:
            # Match transfers where the account is either the source OR destination
            stmt = stmt.where(
                or_(
                    TransferModel.from_account_id == str(account_id),
                    TransferModel.to_account_id == str(account_id),
                )
            )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars().all()]

    def save(self, transfer: Transfer) -> Transfer:
        """
        Persist the Transfer row.

        Must be called BEFORE the transaction legs are saved, because the
        legs have transfer_id FK referencing this transfer's id.
        """
        model = self._to_model(transfer)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def delete(self, transfer_id: UUID, user_id: UUID) -> None:
        """
        Delete the Transfer row only.

        PRECONDITION: caller must have already deleted the transaction legs.
        """
        model = self._session.get(TransferModel, str(transfer_id))
        if model is not None and model.user_id == str(user_id):
            self._session.delete(model)
            self._session.flush()

    # ── Mapping ───────────────────────────────────────────────────────────────

    def _to_domain(self, model: TransferModel) -> Transfer:
        return Transfer(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            from_account_id=UUID(model.from_account_id),
            to_account_id=UUID(model.to_account_id),
            amount=model.amount,
            date=model.date,
            notes=model.notes,
            created_at=model.created_at,
        )

    def _to_model(self, transfer: Transfer) -> TransferModel:
        return TransferModel(
            id=str(transfer.id),
            user_id=str(transfer.user_id),
            from_account_id=str(transfer.from_account_id),
            to_account_id=str(transfer.to_account_id),
            amount=transfer.amount,
            date=transfer.date,
            notes=transfer.notes,
            created_at=transfer.created_at,
        )
