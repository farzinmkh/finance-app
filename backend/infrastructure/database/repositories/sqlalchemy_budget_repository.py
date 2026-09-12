"""SQLAlchemy Budget Repository"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.budget import Budget
from domain.exceptions import ConflictError, NotFoundError
from domain.repositories.budget_repository import BudgetRepository
from infrastructure.database.models import BudgetModel


class SQLAlchemyBudgetRepository(BudgetRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, budget_id: UUID, user_id: UUID) -> Budget | None:
        model = self._session.get(BudgetModel, str(budget_id))
        if model is None or model.user_id != str(user_id):
            return None
        return self._to_domain(model)

    def get_by_category_month(
        self,
        user_id: UUID,
        category_id: UUID,
        month: int,
        year: int,
    ) -> Budget | None:
        stmt = (
            select(BudgetModel)
            .where(BudgetModel.user_id == str(user_id))
            .where(BudgetModel.category_id == str(category_id))
            .where(BudgetModel.month == month)
            .where(BudgetModel.year == year)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def list_by_user(
        self,
        user_id: UUID,
        month: int | None = None,
        year: int | None = None,
    ) -> list[Budget]:
        stmt = (
            select(BudgetModel)
            .where(BudgetModel.user_id == str(user_id))
            .order_by(BudgetModel.year.desc(), BudgetModel.month.desc())
        )
        if month is not None:
            stmt = stmt.where(BudgetModel.month == month)
        if year is not None:
            stmt = stmt.where(BudgetModel.year == year)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars().all()]

    def save(self, budget: Budget) -> Budget:
        model = self._to_model(budget)
        try:
            self._session.add(model)
            self._session.flush()
        except IntegrityError:
            raise ConflictError(
                f"A budget for this category already exists for "
                f"{budget.month:02d}/{budget.year}."
            )
        return self._to_domain(model)

    def update(self, budget: Budget) -> Budget:
        model = self._session.get(BudgetModel, str(budget.id))
        if model is None:
            raise NotFoundError(f"Budget '{budget.id}' not found for update.")
        model.amount = budget.amount
        self._session.flush()
        return self._to_domain(model)

    def delete(self, budget_id: UUID, user_id: UUID) -> None:
        model = self._session.get(BudgetModel, str(budget_id))
        if model is not None and model.user_id == str(user_id):
            self._session.delete(model)
            self._session.flush()

    # ── Mapping ───────────────────────────────────────────────────────────────

    def _to_domain(self, model: BudgetModel) -> Budget:
        return Budget(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            category_id=UUID(model.category_id),
            amount=model.amount,
            month=model.month,
            year=model.year,
            created_at=model.created_at,
        )

    def _to_model(self, budget: Budget) -> BudgetModel:
        return BudgetModel(
            id=str(budget.id),
            user_id=str(budget.user_id),
            category_id=str(budget.category_id),
            amount=budget.amount,
            month=budget.month,
            year=budget.year,
            created_at=budget.created_at,
        )
