"""Update Category Use Case"""
from dataclasses import dataclass
from uuid import UUID

from domain.entities.category import Category
from domain.exceptions import NotFoundError
from domain.repositories.category_repository import CategoryRepository


@dataclass
class UpdateCategoryInput:
    category_id: UUID
    user_id: UUID
    name: str  # the only mutable field; category_type is immutable after creation


class UpdateCategory:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._repo = category_repository

    def execute(self, input_data: UpdateCategoryInput) -> Category:
        """
        Update a category's name.

        category_type is intentionally not updatable. Changing a category
        from income → expense would cause type mismatches on existing
        transactions that use it.

        Raises:
            NotFoundError: if the category does not exist or belongs to a
                           different user.
            DomainValidationError: if the new name is invalid.
            ConflictError: if the new name already exists for this user.
        """
        category = self._repo.get_by_id(input_data.category_id, input_data.user_id)
        if category is None:
            raise NotFoundError(f"Category '{input_data.category_id}' was not found.")

        category.update_name(input_data.name)
        return self._repo.update(category)
