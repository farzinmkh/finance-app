"""
Category API Schemas
======================
Request/response models for the categories endpoints.

category_type is settable on create but never on update — the domain
entity enforces this immutability (Category.update_name() is the only
mutation method), so there is intentionally no category_type field on
UpdateCategoryRequest.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from domain.entities.category import Category, CategoryType


class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category display name.")
    category_type: CategoryType = Field(..., description="'income' or 'expense'.")


class UpdateCategoryRequest(BaseModel):
    """category_type is intentionally not present — it is immutable after creation."""

    name: str = Field(..., min_length=1, max_length=100, description="New category name.")

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be empty or contain only whitespace.")
        return v


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    category_type: CategoryType
    created_at: datetime

    @classmethod
    def from_domain(cls, category: Category) -> "CategoryResponse":
        return cls(
            id=category.id,
            name=category.name,
            category_type=category.category_type,
            created_at=category.created_at,
        )
