"""
Delete Category Use Case
=========================
Deletes a category. Transactions referencing it are NOT deleted — the
database's ON DELETE SET NULL foreign key behaviour sets their category_id
to NULL, leaving them as uncategorised transactions.

This is the correct behaviour for a personal finance app: a user should
not lose their transaction history just because they reorganise their
categories.
"""
from uuid import UUID

from domain.exceptions import NotFoundError
from domain.repositories.category_repository import CategoryRepository


class DeleteCategory:
    def __init__(self, category_repository: CategoryRepository) -> None:
        self._repo = category_repository

    def execute(self, category_id: UUID, user_id: UUID) -> None:
        """
        Delete a category.

        Raises:
            NotFoundError: if the category does not exist or belongs to a
                           different user.
        """
        category = self._repo.get_by_id(category_id, user_id)
        if category is None:
            raise NotFoundError(f"Category '{category_id}' was not found.")

        self._repo.delete(category_id, user_id)
