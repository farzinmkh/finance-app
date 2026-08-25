"""
Category Repository Interface
==============================
Defines the contract for category data access.

The name uniqueness constraint (user cannot have two categories with
the same name) is enforced at the database level (UNIQUE constraint)
and surfaced as a ConflictError by the concrete implementation.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.category import Category, CategoryType


class CategoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, category_id: UUID, user_id: UUID) -> Category | None:
        """
        Return the category if it exists and belongs to user_id.
        Return None if not found OR if it belongs to a different user.
        """
        ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        category_type: CategoryType | None = None,
    ) -> list[Category]:
        """
        Return all categories for the user, optionally filtered by type.
        Ordered by name alphabetically.
        """
        ...

    @abstractmethod
    def save(self, category: Category) -> Category:
        """
        Persist a new category. Does NOT commit.

        Raises:
            ConflictError: if a category with the same name already
                           exists for this user.
        """
        ...

    @abstractmethod
    def update(self, category: Category) -> Category:
        """
        Persist changes to an existing category. Does NOT commit.
        """
        ...

    @abstractmethod
    def delete(self, category_id: UUID, user_id: UUID) -> None:
        """
        Delete the category. Does NOT commit.

        Transactions that reference this category will have their
        category_id set to NULL by the database (ON DELETE SET NULL).
        The application does not need to handle this manually.
        """
        ...
