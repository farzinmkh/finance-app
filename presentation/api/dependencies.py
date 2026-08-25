"""
Shared FastAPI Dependencies
============================
get_current_user() is the single security gate for all protected routes.

It replaces the temporary X-User-Id header used during development.

How it works:
    1. FastAPI's HTTPBearer extracts the token from Authorization: Bearer <token>
    2. decode_access_token() validates the signature and expiry
    3. The user_id from the token's 'sub' claim is used to look up the User
    4. The User object is injected into the route handler

If any step fails → HTTP 401 with WWW-Authenticate: Bearer header.

Why return User (not just UUID)?
    The route handler may need the user's email for logging or response data.
    Returning the full User object is more flexible and avoids a second DB query
    if the email is needed later in the request lifecycle.

Security note:
    Never trust anything in the token payload without verifying the signature
    first. decode_access_token() enforces signature verification before any
    payload data is used.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.exceptions import AuthenticationError
from infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from infrastructure.database.session import get_db
from infrastructure.security.jwt import decode_access_token

# HTTPBearer extracts the token from the Authorization: Bearer header.
# auto_error=False means we get None (not a 403) if the header is absent,
# which lets us return a more informative 401 with our own message.
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the Bearer JWT and return the authenticated User.

    Raises HTTP 401 if:
      - Authorization header is absent
      - Token format is invalid
      - Signature does not match (tampered token)
      - Token has expired
      - User account no longer exists in the database

    This dependency is injected into every protected route:
        @router.get("/accounts")
        def list_accounts(current_user: User = Depends(get_current_user)):
            ...
    """
    _401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a valid Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise _401

    try:
        payload = decode_access_token(credentials.credentials)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise _401

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise _401

    user = SQLAlchemyUserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found. Please register or contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
