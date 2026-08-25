"""Get Category Use Case"""
from uuid import UUID

from domain.entities.category import Category
from domain.exceptions import NotFoundError
from domain.repositories.category_repository import CategoryRepository


class GetCategory:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._repo = category_repository

    def execute(self, category_id: UUID, user_id: UUID) -> Category:
        category = self._repo.get_by_id(category_id, user_id)
        if category is None:
            raise NotFoundError(f"Category '{category_id}' was not found.")
        return category
