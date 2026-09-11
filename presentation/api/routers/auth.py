"""
Auth Router
============
Thin HTTP layer over the existing auth use cases. Contains no business
logic — only request/response translation and dependency wiring.

Login uses FastAPI's OAuth2PasswordRequestForm (form-encoded username +
password), which is what makes Swagger UI's "Authorize" button work with
zero extra client-side code: it POSTs the form directly to this endpoint
and stores the returned access_token for subsequent requests.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from application.use_cases.auth.auth_use_cases import (
    LoginUser,
    RegisterUser,
    RegisterUserInput,
)
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from infrastructure.database.session import get_db
from infrastructure.security.jwt import create_access_token
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.auth import RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account. The password is hashed before storage "
        "and is never returned in any response."
    ),
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """
    Raises (via existing global error handlers):
        422 — invalid email format or password too short (DomainValidationError)
        409 — an account with this email already exists (ConflictError)
    """
    repo = SQLAlchemyUserRepository(db)
    output = RegisterUser(repo).execute(
        RegisterUserInput(email=payload.email, password=payload.password)
    )
    # RegisterUser returns AuthOutput (user_id, email only). Re-fetch the
    # full domain User so the response can include created_at, without
    # widening the shared AuthOutput type used by both register and login.
    user = repo.get_by_id(UUID(output.user_id))
    return UserResponse.from_domain(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and obtain a JWT access token",
    description=(
        "Accepts OAuth2 password-flow form data (username, password). "
        "The 'username' field is the account's email address. "
        "Returns a Bearer access token to use in the Authorization header "
        "of subsequent requests."
    ),
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Raises (via existing global error handlers):
        401 — invalid email or password (AuthenticationError)
    """
    repo = SQLAlchemyUserRepository(db)
    output = LoginUser(repo).execute(email=form_data.username, password=form_data.password)
    token = create_access_token(user_id=output.user_id, email=output.email)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user",
    description="Returns the profile of the user identified by the Bearer token.",
)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Raises (via existing global error handlers):
        401 — missing, invalid, or expired token (AuthenticationError)
    """
    return UserResponse.from_domain(current_user)
