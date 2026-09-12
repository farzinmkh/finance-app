"""SQLAlchemy Category Repository"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.category import Category, CategoryType
from domain.exceptions import ConflictError, NotFoundError
from domain.repositories.category_repository import CategoryRepository
from infrastructure.database.models import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, category_id: UUID, user_id: UUID) -> Category | None:
        model = self._session.get(CategoryModel, str(category_id))
        if model is None or model.user_id != str(user_id):
            return None
        return self._to_domain(model)

    def list_by_user(
        self,
        user_id: UUID,
        category_type: CategoryType | None = None,
    ) -> list[Category]:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.user_id == str(user_id))
            .order_by(CategoryModel.name)
        )
        if category_type is not None:
            stmt = stmt.where(CategoryModel.category_type == category_type.value)
        models = self._session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def save(self, category: Category) -> Category:
        model = self._to_model(category)
        try:
            self._session.add(model)
            self._session.flush()
        except IntegrityError:
            raise ConflictError(
                f"A category named '{category.name}' already exists for this user."
            )
        return self._to_domain(model)

    def update(self, category: Category) -> Category:
        model = self._session.get(CategoryModel, str(category.id))
        if model is None:
            raise NotFoundError(f"Category '{category.id}' not found for update.")
        try:
            model.name = category.name
            self._session.flush()
        except IntegrityError:
            raise ConflictError(
                f"A category named '{category.name}' already exists for this user."
            )
        return self._to_domain(model)

    def delete(self, category_id: UUID, user_id: UUID) -> None:
        model = self._session.get(CategoryModel, str(category_id))
        if model is not None and model.user_id == str(user_id):
            self._session.delete(model)
            self._session.flush()

    # ── Mapping ───────────────────────────────────────────────────────────────

    def _to_domain(self, model: CategoryModel) -> Category:
        return Category(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            name=model.name,
            category_type=CategoryType(model.category_type),
            created_at=model.created_at,
        )

    def _to_model(self, category: Category) -> CategoryModel:
        return CategoryModel(
            id=str(category.id),
            user_id=str(category.user_id),
            name=category.name,
            category_type=category.category_type.value,
            created_at=category.created_at,
        )
