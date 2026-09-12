"""List Categories Use Case"""
from uuid import UUID

from domain.entities.category import Category, CategoryType
from domain.repositories.category_repository import CategoryRepository


class ListCategories:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._repo = category_repository

    def execute(
        self,
        user_id: UUID,
        category_type: CategoryType | None = None,
    ) -> list[Category]:
        """Return all categories for the user, optionally filtered by type."""
        return self._repo.list_by_user(user_id, category_type)
