"""
Delete Transfer Use Case
=========================
Removes a transfer and reverses its balance effects on both accounts.

Deletion order is critical due to FK constraints:

  The database has:
    transactions.transfer_id → transfers.id  (ON DELETE RESTRICT)

  RESTRICT means: if any transaction row references this transfer_id,
  the database will REFUSE to delete the Transfer row.

  Correct deletion order (enforced by this use case):
    1. Reverse from_account balance (add back the amount)
    2. Reverse to_account balance   (subtract the amount)
    3. Delete BOTH transaction legs  ← must happen BEFORE step 4
    4. Delete the Transfer row

  If steps 3 and 4 were swapped, the database would raise an IntegrityError
  when we tried to delete the transfer (because the legs still reference it).

Why are balances reversed BEFORE deleting the legs?
  The legs are needed only to identify which transfer amount to reverse.
  Since we already have the transfer object with the amount, we reverse
  using the transfer.amount directly — we don't need to read the legs.
  The leg deletion is purely for referential integrity.
"""

from uuid import UUID

from domain.exceptions import NotFoundError
from domain.repositories.account_repository import AccountRepository
from domain.repositories.transaction_repository import TransactionRepository
from domain.repositories.transfer_repository import TransferRepository


class DeleteTransfer:
    def __init__(
        self,
        transfer_repository: TransferRepository,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ) -> None:
        self._transfer_repo = transfer_repository
        self._account_repo = account_repository
        self._transaction_repo = transaction_repository

    def execute(self, transfer_id: UUID, user_id: UUID) -> None:
        """
        Delete the transfer and reverse both account balances.

        All operations are within one session. get_db() commits if this
        method returns normally, or rolls back if it raises an exception.

        Raises:
            NotFoundError: if the transfer does not exist or belongs to a
                           different user.
        """
        # ── Step 1: Verify the transfer exists and belongs to this user ───────
        transfer = self._transfer_repo.get_by_id(transfer_id, user_id)
        if transfer is None:
            raise NotFoundError(f"Transfer '{transfer_id}' was not found.")

        # ── Step 2: Get both accounts ─────────────────────────────────────────
        # Because accounts → transfers has ON DELETE RESTRICT, both accounts
        # are guaranteed to still exist when a transfer references them.
        # But we add defensive None checks for safety.
        from_account = self._account_repo.get_by_id(transfer.from_account_id, user_id)
        to_account = self._account_repo.get_by_id(transfer.to_account_id, user_id)

        if from_account is None or to_account is None:
            raise NotFoundError(
                "One or both accounts referenced by this transfer no longer exist."
            )

        # ── Step 3: Reverse the balance effects ───────────────────────────────
        # Undo exactly what CreateTransfer did:
        #   from_account had money subtracted → add it back
        #   to_account had money added        → subtract it back
        from_account.current_balance += transfer.amount
        to_account.current_balance -= transfer.amount
        self._account_repo.update(from_account)
        self._account_repo.update(to_account)

        # ── Step 4: Delete the transaction legs FIRST ─────────────────────────
        # REQUIRED before deleting the Transfer row.
        # transactions.transfer_id has ON DELETE RESTRICT → the DB refuses to
        # delete the Transfer while rows still reference it.
        self._transaction_repo.delete_by_transfer_id(transfer_id)

        # ── Step 5: Delete the Transfer record ───────────────────────────────
        # Now that no transaction rows reference this transfer_id, the
        # RESTRICT constraint is satisfied and this delete will succeed.
        self._transfer_repo.delete(transfer_id, user_id)
