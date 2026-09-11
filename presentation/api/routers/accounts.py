"""
Accounts Router
================
Thin HTTP layer over the existing account use cases. No business logic,
no direct SQLAlchemy queries — everything is delegated to the application
layer, which is delegated to the domain layer.

user_id is NEVER accepted from the client. It always comes from the
authenticated User provided by get_current_user().
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from application.use_cases.accounts.create_account import (
    CreateAccount,
    CreateAccountInput,
)
from application.use_cases.accounts.delete_account import DeleteAccount
from application.use_cases.accounts.get_account import GetAccount
from application.use_cases.accounts.list_accounts import ListAccounts
from application.use_cases.accounts.update_account import (
    UpdateAccount,
    UpdateAccountInput,
)
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.accounts import (
    AccountResponse,
    CreateAccountRequest,
    UpdateAccountRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
def create_account(
    payload: CreateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountResponse:
    """Raises 422 (DomainValidationError) for an invalid name/currency."""
    repo = SQLAlchemyAccountRepository(db)
    account = CreateAccount(repo).execute(
        CreateAccountInput(
            user_id=current_user.id,
            name=payload.name,
            account_type=payload.account_type,
            currency=payload.currency,
            opening_balance=payload.opening_balance,
        )
    )
    return AccountResponse.from_domain(account)


@router.get(
    "",
    response_model=list[AccountResponse],
    summary="List all accounts for the current user",
)
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AccountResponse]:
    repo = SQLAlchemyAccountRepository(db)
    accounts = ListAccounts(repo).execute(current_user.id)
    return [AccountResponse.from_domain(a) for a in accounts]


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Get a single account by ID",
)
def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountResponse:
    """Raises 404 if the account does not exist or belongs to another user."""
    repo = SQLAlchemyAccountRepository(db)
    account = GetAccount(repo).execute(account_id, current_user.id)
    return AccountResponse.from_domain(account)


@router.put(
    "/{account_id}",
    response_model=AccountResponse,
    summary="Update an account's name and/or type",
)
def update_account(
    account_id: UUID,
    payload: UpdateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountResponse:
    """Raises 404 if not found/owned, 422 if the new name is invalid."""
    repo = SQLAlchemyAccountRepository(db)
    account = UpdateAccount(repo).execute(
        UpdateAccountInput(
            account_id=account_id,
            user_id=current_user.id,
            name=payload.name,
            account_type=payload.account_type,
        )
    )
    return AccountResponse.from_domain(account)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an account",
)
def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Raises:
        404 — account not found or belongs to another user.
        409 — account still has transactions or transfers linked to it.
    """
    repo = SQLAlchemyAccountRepository(db)
    DeleteAccount(repo).execute(account_id, current_user.id)
