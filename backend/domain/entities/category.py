"""
Category Domain Entity
=======================
Categories classify transactions — e.g. "Groceries", "Salary", "Rent".

Design decisions:
-----------------
1. category_type is IMMUTABLE after creation. If we allowed changing a
   category from income → expense, all transactions using it would have
   a type mismatch. Enforcing immutability avoids that integrity problem.

2. Names are unique per user (enforced at the database level via UNIQUE
   constraint, and at the application level via ConflictError).

3. update_name() keeps the name-validation rules inside the entity.
   The use case calls it rather than setting .name directly.

Dependency rule: imports only stdlib and domain/exceptions.py.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from domain.exceptions import DomainValidationError


class CategoryType(str, Enum):
    """
    Whether a category is for income or expense transactions.

    Inheriting from str makes this JSON-serialisable and lets Pydantic
    and FastAPI use the string values directly in API schemas.

    A category's type must match any transaction it is assigned to:
      income category  → only usable on income transactions
      expense category → only usable on expense transactions
    """

    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class Category:
    """
    A user-owned label for classifying transactions.

    Do not construct this directly. Use Category.create() to ensure
    business rules are validated before the object is built.
    """

    id: UUID
    user_id: UUID
    name: str
    category_type: CategoryType
    created_at: datetime

    # ── Factory method ──────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: str,
        category_type: CategoryType,
    ) -> "Category":
        """
        Create a new Category with validated fields.

        Raises:
            DomainValidationError: if the name is invalid.
        """
        return cls(
            id=uuid4(),
            user_id=user_id,
            name=cls._validate_name(name),
            category_type=category_type,
            created_at=datetime.now(timezone.utc),
        )

    # ── Mutation methods ─────────────────────────────────────────────────────

    def update_name(self, new_name: str) -> None:
        """
        Update the category display name.

        category_type is intentionally NOT updatable. Changing a category
        from income → expense would leave existing transactions with a
        mismatched category type, breaking a core business rule.

        Raises:
            DomainValidationError: if the new name is invalid.
        """
        self.name = self._validate_name(new_name)

    # ── Private validation ───────────────────────────────────────────────────

    @staticmethod
    def _validate_name(name: str) -> str:
        stripped = name.strip()
        if not stripped:
            raise DomainValidationError(
                "Category name must not be empty or contain only whitespace."
            )
        if len(stripped) > 100:
            raise DomainValidationError(
                f"Category name must not exceed 100 characters (got {len(stripped)})."
            )
        return stripped
