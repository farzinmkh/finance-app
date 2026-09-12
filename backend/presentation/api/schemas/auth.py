"""
Auth API Schemas
=================
Pydantic models for the authentication endpoints.

Note on password validation:
    We deliberately do NOT duplicate the "password must be at least 8
    characters" rule here with a Pydantic Field(min_length=8). That rule
    is a business rule owned by RegisterUser/DomainValidationError, which
    already maps to HTTP 422 via the existing error handlers. Duplicating
    it here would mean two different validation paths could disagree, and
    it would move a business rule into the presentation layer. This schema
    only enforces structural constraints (non-empty, reasonable length).

Note on email:
    We intentionally use a plain `str` rather than Pydantic's `EmailStr`.
    EmailStr requires the optional `email-validator` dependency, which is
    not part of this project's dependency set. RegisterUser already
    validates the email format ("must contain '@'") in the domain layer,
    so basic format checking is not lost — it simply lives in the correct
    layer instead of adding a new dependency for it.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from domain.entities.user import User


# ── Request schemas ───────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register."""

    email: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Email address. Used as the login identifier.",
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description=(
            "Plaintext password (never stored). Must be at least 8 "
            "characters — enforced by the application layer."
        ),
    )


# ── Response schemas ─────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """
    The user representation returned by the API.

    Never includes hashed_password or any other internal/security field.
    """

    id: UUID
    email: str
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(id=user.id, email=user.email, created_at=user.created_at)


class TokenResponse(BaseModel):
    """
    Payload returned by POST /api/v1/auth/login.

    Shape matches the OAuth2 Bearer token convention that FastAPI's
    Swagger "Authorize" button expects.
    """

    access_token: str
    token_type: str = "bearer"
