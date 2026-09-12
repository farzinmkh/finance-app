"""
Transfers Router
==================
Thin HTTP layer over the existing transfer use cases. No business logic,
no direct SQLAlchemy queries — everything is delegated to the application
layer, which is delegated to the domain layer.

user_id is NEVER accepted from the client. It always comes from the
authenticated User provided by get_current_user().

No PUT/update endpoint exists here on purpose — see UpdateTransfer's
absence in the application layer: updating a transfer's amount would
require reversing and reapplying both account balances and both
transaction legs, which is equivalent to delete + recreate. Clients
should DELETE then POST a new transfer instead.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from application.use_cases.transfers.create_transfer import (
    CreateTransfer,
    CreateTransferInput,
)
from application.use_cases.transfers.delete_transfer import DeleteTransfer
from application.use_cases.transfers.get_transfer import GetTransfer
from application.use_cases.transfers.list_transfers import ListTransfers
from domain.entities.user import User
from infrastructure.database.repositories.sqlalchemy_account_repository import (
    SQLAlchemyAccountRepository,
)
from infrastructure.database.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)
from infrastructure.database.repositories.sqlalchemy_transfer_repository import (
    SQLAlchemyTransferRepository,
)
from infrastructure.database.session import get_db
from presentation.api.dependencies import get_current_user
from presentation.api.schemas.transfers import CreateTransferRequest, TransferResponse

router = APIRouter()


@router.post(
    "",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transfer between two accounts",
)
def create_transfer(
    payload: CreateTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransferResponse:
    """
    Records a transfer and atomically:
      - creates an expense leg on from_account_id
      - creates an income leg on to_account_id
      - updates both account balances

    All writes happen in one database transaction (committed together by
    get_db when this request returns successfully).

    Raises:
        404 — source or destination account not found / not owned by the
              current user.
        422 — from_account_id == to_account_id, or amount is not a
              positive Decimal.
    """
    transfer_repo = SQLAlchemyTransferRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    transaction_repo = SQLAlchemyTransactionRepository(db)

    transfer = CreateTransfer(
        transfer_repository=transfer_repo,
        account_repository=account_repo,
        transaction_repository=transaction_repo,
    ).execute(
        CreateTransferInput(
            user_id=current_user.id,
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            date=payload.date,
            notes=payload.notes,
        )
    )
    return TransferResponse.from_domain(transfer)


@router.get(
    "",
    response_model=list[TransferResponse],
    summary="List transfers for the current user",
)
def list_transfers(
    account_id: UUID | None = Query(
        default=None,
        description="Filter to transfers where this account is the source OR destination.",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TransferResponse]:
    """Ordered by date descending, then created_at descending."""
    repo = SQLAlchemyTransferRepository(db)
    transfers = ListTransfers(repo).execute(current_user.id, account_id)
    return [TransferResponse.from_domain(t) for t in transfers]


@router.get(
    "/{transfer_id}",
    response_model=TransferResponse,
    summary="Get a single transfer by ID",
)
def get_transfer(
    transfer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransferResponse:
    """Raises 404 if the transfer does not exist or belongs to another user."""
    repo = SQLAlchemyTransferRepository(db)
    transfer = GetTransfer(repo).execute(transfer_id, current_user.id)
    return TransferResponse.from_domain(transfer)


@router.delete(
    "/{transfer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a transfer",
)
def delete_transfer(
    transfer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Deletes the transfer and reverses its effect on both account balances.
    Both transaction legs are deleted along with it.

    Raises 404 if the transfer does not exist or belongs to another user.
    """
    transfer_repo = SQLAlchemyTransferRepository(db)
    account_repo = SQLAlchemyAccountRepository(db)
    transaction_repo = SQLAlchemyTransactionRepository(db)

    DeleteTransfer(
        transfer_repository=transfer_repo,
        account_repository=account_repo,
        transaction_repository=transaction_repo,
    ).execute(transfer_id, current_user.id)
