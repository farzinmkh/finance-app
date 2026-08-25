"""
User Domain Entity
==================
Represents a registered user of the application.

This entity is intentionally minimal in the current phase.
Authentication methods (verify_password, etc.) will be added
when the authentication feature is implemented.

Dependency rule: This file imports NOTHING outside the standard library.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    """
    A registered user who owns accounts, transactions, and categories.

    All financial data in the application is scoped to a User.
    The user_id is the primary authorization key — every database query
    that retrieves financial data must filter by user_id.

    Fields:
        id              System-generated UUID. Never set by the user.
        email           Unique email address. Used for login.
        hashed_password The bcrypt hash of the password. Never the plaintext.
        created_at      UTC timestamp of when the account was created.
    """

    id: UUID
    email: str
    hashed_password: str
    created_at: datetime
