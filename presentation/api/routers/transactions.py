"""
Transactions Router
=====================
Thin HTTP layer over the existing transaction use cases. No business logic,
no direct SQLAlchemy queries — everything is delegated to the application
layer, which is delegated to the domain layer.

user_id is NEVER accepted from the client. It always comes from the
authenticated User provided by get_current_user().

Query-string filters on GET /transactions mirror ListTransactionsFilters:
account_id, transaction_type, category_id, date_from, date_to, plus
page/page_size for pagination. All are optional.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from application.use_cases.transactions.create_transaction import (
    CreateTransaction,
    CreateTransactionInput,
)
from application.use_cases.transactions.delete_transaction import DeleteTransaction
from application.use_cases.transactions.get_transaction import GetTransaction
from application.use_cases.transactions.list_transactions import (
    ListTransactions,
    ListTransactionsFilters,
)
from application.use_cases.transactions.update_transaction import (
    UpdateTransaction,
    UpdateTransactionInput,
)
from domain.entities.transaction import TransactionType
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from infrastructure.database.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from infrastructure.database.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.transactions import (
    CreateTransactionRequest,
    TransactionResponse,
    TransactionsPageResponse,
    UpdateTransactionRequest,
)

router = APIRouter()


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction",
)
def create_transaction(
    payload: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """
    Records a transaction and atomically updates the owning account's balance.

    Raises:
        404 — account or category not found / not owned by the current user.
        422 — invalid amount, or category type does not match transaction type.
    """
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)

    transaction = CreateTransaction(
        transaction_repository=transaction_repo,
        account_repository=account_repo,
        category_repository=category_repo,
    ).execute(
        CreateTransactionInput(
            user_id=current_user.id,
            account_id=payload.account_id,
            transaction_type=payload.transaction_type,
            amount=payload.amount,
            date=payload.date,
            category_id=payload.category_id,
            notes=payload.notes,
        )
    )
    return TransactionResponse.from_domain(transaction)


@router.get(
    "",
    response_model=TransactionsPageResponse,
    summary="List transactions for the current user (paginated, filterable)",
)
def list_transactions(
    account_id: UUID | None = Query(default=None, description="Filter by account."),
    transaction_type: TransactionType | None = Query(
        default=None, description="Filter by 'income' or 'expense'."
    ),
    category_id: UUID | None = Query(default=None, description="Filter by category."),
    date_from: date | None = Query(default=None, description="Inclusive start date."),
    date_to: date | None = Query(default=None, description="Inclusive end date."),
    page: int = Query(default=1, ge=1, description="1-indexed page number."),
    page_size: int = Query(default=20, ge=1, le=200, description="Items per page."),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionsPageResponse:
    """
    All filters are optional and combine with AND logic.
    Results are ordered by date descending, then created_at descending.
    """
    repo = SQLAlchemyTransactionRepository(db)
    result = ListTransactions(repo).execute(
        ListTransactionsFilters(
            user_id=current_user.id,
            account_id=account_id,
            transaction_type=transaction_type,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
    )
    return TransactionsPageResponse.from_page(result)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get a single transaction by ID",
)
def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Raises 404 if the transaction does not exist or belongs to another user."""
    repo = SQLAlchemyTransactionRepository(db)
    transaction = GetTransaction(repo).execute(transaction_id, current_user.id)
    return TransactionResponse.from_domain(transaction)


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update a transaction",
)
def update_transaction(
    transaction_id: UUID,
    payload: UpdateTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """
    Updates the given fields and atomically corrects the account balance
    if amount or transaction_type changed.

    Category handling (see UpdateTransactionRequest docs):
        clear_category=true        → category is set to null
        category_id=<uuid>         → category is changed to that id
        neither provided           → category is left unchanged

    Raises:
        404 — transaction, account, or new category not found / not owned.
        422 — invalid new amount, or category type mismatch.
        422 (TransactionLockedError) — transaction is a transfer leg;
            delete and recreate the transfer instead.
    """
    update_category = payload.clear_category or payload.category_id is not None
    new_category_id = None if payload.clear_category else payload.category_id

    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)

    transaction = UpdateTransaction(
        transaction_repository=transaction_repo,
        account_repository=account_repo,
        category_repository=category_repo,
    ).execute(
        UpdateTransactionInput(
            transaction_id=transaction_id,
            user_id=current_user.id,
            amount=payload.amount,
            transaction_type=payload.transaction_type,
            date=payload.date,
            notes=payload.notes,
            update_category=update_category,
            new_category_id=new_category_id,
        )
    )
    return TransactionResponse.from_domain(transaction)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transaction",
)
def delete_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Deletes the transaction and reverses its effect on the account balance.

    Raises:
        404 — transaction not found or belongs to another user.
        422 (TransactionLockedError) — transaction is a transfer leg;
            use the transfer delete endpoint instead.
    """
    transaction_repo = SQLAlchemyTransactionRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    DeleteTransaction(
        transaction_repository=transaction_repo,
        account_repository=account_repo,
    ).execute(transaction_id, current_user.id)
