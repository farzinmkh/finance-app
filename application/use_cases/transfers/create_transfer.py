"""
Create Transfer Use Case
=========================
Records a transfer between two accounts and atomically updates both balances.

This is the most operationally complex use case in the application.
Five writes must succeed together or fail together:

  1. INSERT transfers row                          (TransferRepository.save)
  2. INSERT expense transaction on from_account    (TransactionRepository.save)
  3. INSERT income  transaction on to_account      (TransactionRepository.save)
  4. UPDATE from_account.current_balance -= amount (AccountRepository.update)
  5. UPDATE to_account.current_balance   += amount (AccountRepository.update)

All five happen within one SQLAlchemy session. get_db() commits only when
the route handler returns successfully. If anything raises an exception,
get_db() rolls back — all five writes are cancelled together.

The DB-level atomicity guarantee means partial transfers are structurally
impossible, not just unlikely. This is the correct approach for financial data.

Why save the Transfer BEFORE the transaction legs?
  The legs have a FK: transactions.transfer_id → transfers.id
  If we inserted the legs first, the FK would fail (referencing a
  transfer_id that doesn't exist yet). Transfer row must come first.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.entities.transfer import Transfer
from domain.entities.transaction import Transaction, TransactionType
from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository
from domain.repositories.transaction_repository import TransactionRepository
from domain.repositories.transfer_repository import TransferRepository


@dataclass
class CreateTransferInput:
    user_id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    date: date
    notes: str | None = None


class CreateTransfer:
    def __init__(
        self,
        transfer_repository: TransferRepository,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._transfer_repo = transfer_repository
        self._account_repo = account_repository
        self._transaction_repo = transaction_repository

    def execute(self, input_data: CreateTransferInput) -> Transfer:
        """
        Create the transfer and all side effects atomically.

        Raises:
            NotFoundError: if either account does not exist or does not
                           belong to the authenticated user.
            DomainValidationError: if from == to, or amount <= 0, or
                                   amount is not a Decimal.
        """
        # ── Step 1: Verify both accounts ─────────────────────────────────────
        # Note: get_by_id returns None for both "not found" AND "wrong user".
        # The error message says "not found" in both cases — deliberate.
        from_account = self._account_repo.get_by_id(
            input_data.from_account_id, input_data.user_id
        )
        if from_account is None:
            raise NotFoundError(
                f"Source account '{input_data.from_account_id}' was not found."
            )

        to_account = self._account_repo.get_by_id(
            input_data.to_account_id, input_data.user_id
        )
        if to_account is None:
            raise NotFoundError(
                f"Destination account '{input_data.to_account_id}' was not found."
            )

        # ── Step 2: Create and validate the Transfer entity ───────────────────
        # Transfer.create() enforces: from != to, amount > 0, amount is Decimal.
        # These domain rules are checked before any DB write.
        transfer = Transfer.create(
            user_id=input_data.user_id,
            from_account_id=input_data.from_account_id,
            to_account_id=input_data.to_account_id,
            amount=input_data.amount,
            date=input_data.date,
            notes=input_data.notes,
        )

        # ── Step 3: Persist the Transfer row FIRST ────────────────────────────
        # The transaction legs have a FK on transfer_id. The transfer must
        # exist in the DB before we can insert rows that reference it.
        saved_transfer = self._transfer_repo.save(transfer)

        # ── Step 4: Create the two transaction legs ───────────────────────────
        #
        # Expense leg: money LEAVING the source account
        expense_leg = Transaction.create(
            account_id=saved_transfer.from_account_id,
            user_id=saved_transfer.user_id,
            transaction_type=TransactionType.EXPENSE,
            amount=saved_transfer.amount,
            date=saved_transfer.date,
            notes=saved_transfer.notes,
            transfer_id=saved_transfer.id,   # marks this as a transfer leg (locked)
        )
        # Income leg: money ARRIVING at the destination account
        income_leg = Transaction.create(
            account_id=saved_transfer.to_account_id,
            user_id=saved_transfer.user_id,
            transaction_type=TransactionType.INCOME,
            amount=saved_transfer.amount,
            date=saved_transfer.date,
            notes=saved_transfer.notes,
            transfer_id=saved_transfer.id,   # marks this as a transfer leg (locked)
        )

        self._transaction_repo.save(expense_leg)
        self._transaction_repo.save(income_leg)

        # ── Step 5: Update both account balances ──────────────────────────────
        #
        # from_account loses the amount (expense)
        from_account.current_balance -= saved_transfer.amount
        self._account_repo.update(from_account)

        # to_account gains the amount (income)
        to_account.current_balance += saved_transfer.amount
        self._account_repo.update(to_account)

        return saved_transfer
