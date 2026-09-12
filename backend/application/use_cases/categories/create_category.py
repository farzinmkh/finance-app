"""
Create Category Use Case
"""
from dataclasses import dataclass
from uuid import UUID

from domain.entities.category import Category, CategoryType
from domain.repositories.category_repository import CategoryRepository


@dataclass
class CreateCategoryInput:
    user_id: UUID
    name: str
    category_type: CategoryType


class CreateCategory:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._repo = category_repository

    def execute(self, input_data: CreateCategoryInput) -> Category:
        """
        Create and persist a new category.

        Raises:
            DomainValidationError: if the name is invalid (via Category.create).
            ConflictError: if a category with this name already exists for the user.
        """
        category = Category.create(
            user_id=input_data.user_id,
            name=input_data.name,
            category_type=input_data.category_type,
        )
        return self._repo.save(category)
