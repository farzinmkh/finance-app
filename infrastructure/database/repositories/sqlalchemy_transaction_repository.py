"""SQLAlchemy Transaction Repository — including dashboard aggregation queries."""
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from domain.entities.transaction import Transaction, TransactionType
from domain.exceptions import NotFoundError
from domain.repositories.transaction_repository import CategoryTotal, TransactionRepository
from infrastructure.database.models import TransactionModel


class SQLAlchemyTransactionRepository(TransactionRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Reads ─────────────────────────────────────────────────────────────────

    def get_by_id(self, transaction_id: UUID, user_id: UUID) -> Transaction | None:
        model = self._session.get(TransactionModel, str(transaction_id))
        if model is None or model.user_id != str(user_id):
            return None
        return self._to_domain(model)

    def list_by_filters(
        self,
        user_id: UUID,
        account_id: UUID | None = None,
        transaction_type: TransactionType | None = None,
        category_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Transaction]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.user_id == str(user_id))
            .order_by(TransactionModel.date.desc(), TransactionModel.created_at.desc())
        )
        if account_id is not None:
            stmt = stmt.where(TransactionModel.account_id == str(account_id))
        if transaction_type is not None:
            stmt = stmt.where(TransactionModel.transaction_type == transaction_type.value)
        if category_id is not None:
            stmt = stmt.where(TransactionModel.category_id == str(category_id))
        if date_from is not None:
            stmt = stmt.where(TransactionModel.date >= date_from)
        if date_to is not None:
            stmt = stmt.where(TransactionModel.date <= date_to)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars().all()]

    def list_recent(self, user_id: UUID, limit: int = 10) -> list[Transaction]:
        stmt = (
            select(TransactionModel)
            .where(TransactionModel.user_id == str(user_id))
            .order_by(TransactionModel.date.desc(), TransactionModel.created_at.desc())
            .limit(limit)
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars().all()]

    # ── Dashboard aggregations ────────────────────────────────────────────────

    def get_period_income_total(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        """
        SUM of income amounts, excluding transfer legs.

        func.sum() returns None when no rows match → we normalise to Decimal("0").
        Using COALESCE in SQL would mix Decimal and int types; Python fallback is cleaner.
        """
        stmt = (
            select(func.sum(TransactionModel.amount))
            .where(TransactionModel.user_id == str(user_id))
            .where(TransactionModel.transaction_type == TransactionType.INCOME.value)
            .where(TransactionModel.transfer_id.is_(None))   # exclude transfer legs
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date <= date_to)
        )
        result = self._session.execute(stmt).scalar()
        return result if result is not None else Decimal("0")

    def get_period_expense_total(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
    ) -> Decimal:
        stmt = (
            select(func.sum(TransactionModel.amount))
            .where(TransactionModel.user_id == str(user_id))
            .where(TransactionModel.transaction_type == TransactionType.EXPENSE.value)
            .where(TransactionModel.transfer_id.is_(None))   # exclude transfer legs
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date <= date_to)
        )
        result = self._session.execute(stmt).scalar()
        return result if result is not None else Decimal("0")

    def get_top_expense_categories(
        self,
        user_id: UUID,
        date_from: date,
        date_to: date,
        limit: int = 5,
    ) -> list[CategoryTotal]:
        """
        Group expense transactions by category, return top N by total.

        Groups uncategorized transactions (category_id IS NULL) together
        as a single CategoryTotal with category_id=None.
        Transfer legs are excluded.
        """
        stmt = (
            select(
                TransactionModel.category_id,
                func.sum(TransactionModel.amount).label("total_amount"),
            )
            .where(TransactionModel.user_id == str(user_id))
            .where(TransactionModel.transaction_type == TransactionType.EXPENSE.value)
            .where(TransactionModel.transfer_id.is_(None))
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date <= date_to)
            .group_by(TransactionModel.category_id)
            .order_by(func.sum(TransactionModel.amount).desc())
            .limit(limit)
        )
        rows = self._session.execute(stmt).all()
        return [
            CategoryTotal(
                category_id=UUID(row.category_id) if row.category_id else None,
                total_amount=row.total_amount if row.total_amount is not None else Decimal("0"),
            )
            for row in rows
        ]

    # ── Writes ────────────────────────────────────────────────────────────────

    def save(self, transaction: Transaction) -> Transaction:
        model = self._to_model(transaction)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def update(self, transaction: Transaction) -> Transaction:
        model = self._session.get(TransactionModel, str(transaction.id))
        if model is None:
            raise NotFoundError(f"Transaction '{transaction.id}' not found for update.")
        model.amount = transaction.amount
        model.transaction_type = transaction.transaction_type.value
        model.category_id = str(transaction.category_id) if transaction.category_id else None
        model.date = transaction.date
        model.notes = transaction.notes
        self._session.flush()
        return self._to_domain(model)

    def delete(self, transaction_id: UUID, user_id: UUID) -> None:
        model = self._session.get(TransactionModel, str(transaction_id))
        if model is not None and model.user_id == str(user_id):
            self._session.delete(model)
            self._session.flush()

    def delete_by_transfer_id(self, transfer_id: UUID) -> None:
        stmt = delete(TransactionModel).where(
            TransactionModel.transfer_id == str(transfer_id)
        )
        self._session.execute(stmt)
        self._session.flush()

    # ── Mapping ───────────────────────────────────────────────────────────────

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=UUID(model.id),
            account_id=UUID(model.account_id),
            user_id=UUID(model.user_id),
            category_id=UUID(model.category_id) if model.category_id else None,
            transaction_type=TransactionType(model.transaction_type),
            amount=model.amount,
            date=model.date,
            notes=model.notes,
            transfer_id=UUID(model.transfer_id) if model.transfer_id else None,
            created_at=model.created_at,
        )

    def _to_model(self, transaction: Transaction) -> TransactionModel:
        return TransactionModel(
            id=str(transaction.id),
            account_id=str(transaction.account_id),
            user_id=str(transaction.user_id),
            category_id=str(transaction.category_id) if transaction.category_id else None,
            transaction_type=transaction.transaction_type.value,
            amount=transaction.amount,
            date=transaction.date,
            notes=transaction.notes,
            transfer_id=str(transaction.transfer_id) if transaction.transfer_id else None,
            created_at=transaction.created_at,
        )

    def get_category_month_spending(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Decimal:
        """
        Total expense spending for one category in one calendar month.

        Uses an inclusive date range (first day through last day of month)
        rather than SQL date functions, which ensures correct behaviour
        across both SQLite and PostgreSQL.
        """
        import calendar
        from datetime import date as date_cls
        date_from = date_cls(year, month, 1)
        date_to = date_cls(year, month, calendar.monthrange(year, month)[1])

        stmt = (
            select(func.sum(TransactionModel.amount))
            .where(TransactionModel.user_id == str(user_id))
            .where(TransactionModel.category_id == str(category_id))
            .where(TransactionModel.transaction_type == TransactionType.EXPENSE.value)
            .where(TransactionModel.transfer_id.is_(None))
            .where(TransactionModel.date >= date_from)
            .where(TransactionModel.date <= date_to)
        )
        result = self._session.execute(stmt).scalar()
        return result if result is not None else Decimal("0")
