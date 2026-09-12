"""
Categories Router
==================
Thin HTTP layer over the existing category use cases.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.use_cases.categories.create_category import (
    CreateCategory,
    CreateCategoryInput,
)
from application.use_cases.categories.delete_category import DeleteCategory
from application.use_cases.categories.get_category import GetCategory
from application.use_cases.categories.list_categories import ListCategories
from application.use_cases.categories.update_category import (
    UpdateCategory,
    UpdateCategoryInput,
)
from domain.entities.category import CategoryType
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.categories import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
)
def create_category(
    payload: CreateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Raises 409 if a category with this name already exists for the user."""
    repo = SQLAlchemyCategoryRepository(db)
    category = CreateCategory(repo).execute(
        CreateCategoryInput(
            user_id=current_user.id,
            name=payload.name,
            category_type=payload.category_type,
        )
    )
    return CategoryResponse.from_domain(category)


@router.get(
    "",
    response_model=list[CategoryResponse],
    summary="List all categories for the current user",
)
def list_categories(
    category_type: CategoryType | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CategoryResponse]:
    """Optionally filter by category type (income or expense)."""
    repo = SQLAlchemyCategoryRepository(db)
    categories = ListCategories(repo).execute(current_user.id, category_type)
    return [CategoryResponse.from_domain(c) for c in categories]


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get a single category by ID",
)
def get_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """Raises 404 if the category does not exist or belongs to another user."""
    repo = SQLAlchemyCategoryRepository(db)
    category = GetCategory(repo).execute(category_id, current_user.id)
    return CategoryResponse.from_domain(category)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category's name",
)
def update_category(
    category_id: UUID,
    payload: UpdateCategoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CategoryResponse:
    """
    Raises:
        404 — category not found or belongs to another user.
        409 — new name already exists for this user.
        422 — new name is invalid.
    """
    repo = SQLAlchemyCategoryRepository(db)
    category = UpdateCategory(repo).execute(
        UpdateCategoryInput(
            category_id=category_id,
            user_id=current_user.id,
            name=payload.name,
        )
    )
    return CategoryResponse.from_domain(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
)
def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Raises 404 if the category does not exist or belongs to another user.

    Transactions that reference this category will have their category_id
    set to NULL by the database (ON DELETE SET NULL) — they remain in the
    database as uncategorized transactions.
    """
    repo = SQLAlchemyCategoryRepository(db)
    DeleteCategory(repo).execute(category_id, current_user.id)
