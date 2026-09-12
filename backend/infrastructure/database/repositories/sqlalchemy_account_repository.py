"""
SQLAlchemy Account Repository
==============================
Concrete implementation of AccountRepository using SQLAlchemy ORM.

This is the only file in the project that:
- Executes SQL queries for accounts
- Knows about AccountModel (the ORM table class)
- Translates between AccountModel ↔ Account (domain entity)

What this file must NOT contain:
- Business rules (those live in domain/entities/account.py)
- HTTP concerns (those live in presentation/api/)
- Use case orchestration (that lives in application/use_cases/)

The mapping methods (_to_domain, _to_model) are the bridge between
the two representations. They are private to this class because no other
code should need to perform this mapping.

Note on session.flush() vs session.commit():
---------------------------------------------
Repository methods call session.flush() NOT session.commit().

flush():  Sends the SQL to the database as part of the current transaction,
          but does NOT commit. The changes are visible within this session
          but not yet permanent. If another part of the same request fails,
          everything is rolled back together.

commit(): Makes changes permanent. This is called by get_db() after the
          entire request succeeds. Not the repository's responsibility.

This distinction is what enables atomicity. The CreateTransfer use case,
for example, will flush two account updates and two transaction inserts —
they all go through as one commit when the route returns successfully.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.entities.account import Account, AccountType
from domain.exceptions import ConflictError, NotFoundError
from domain.repositories.account_repository import AccountRepository
from infrastructure.database.models import AccountModel


class SQLAlchemyAccountRepository(AccountRepository):
    """
    SQLAlchemy-backed implementation of AccountRepository.

    Receives an active Session via constructor injection.
    The Session is provided by the get_db() FastAPI dependency.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── Public interface (implements AccountRepository) ──────────────────────

    def get_by_id(self, account_id: UUID, user_id: UUID) -> Account | None:
        """
        Fetch an account by ID, enforcing user ownership.

        Uses session.get() for primary-key lookups — SQLAlchemy uses the
        identity map (in-session cache) first, falling back to a database
        query if needed. This is slightly more efficient than a full SELECT
        for single-row lookups by primary key.
        """
        model = self._session.get(AccountModel, str(account_id))

        # Check both existence AND ownership in one step.
        # Returning None for "wrong user" is identical to "not found"
        # from the caller's perspective — deliberate information hiding.
        if model is None or model.user_id != str(user_id):
            return None

        return self._to_domain(model)

    def list_by_user(self, user_id: UUID) -> list[Account]:
        """
        Fetch all accounts for a user, ordered by creation date (oldest first).

        Uses the SQLAlchemy 2.x select() style — the recommended approach
        in SQLAlchemy 2.0+. The older session.query() style still works but
        is considered legacy.
        """
        stmt = (
            select(AccountModel)
            .where(AccountModel.user_id == str(user_id))
            .order_by(AccountModel.created_at)
        )
        models = self._session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def save(self, account: Account) -> Account:
        """
        Persist a new account.

        session.add() registers the object with the session.
        session.flush() sends the INSERT to the database within the current
        transaction, making it visible to subsequent queries in the same
        session without committing.
        """
        model = self._to_model(account)
        self._session.add(model)
        self._session.flush()
        return self._to_domain(model)

    def update(self, account: Account) -> Account:
        """
        Persist changes to an existing account.

        Fetches the existing model by primary key, applies changes, then
        flushes. SQLAlchemy's change tracking (Unit of Work) detects the
        modified fields and generates an UPDATE statement for only those.
        """
        model = self._session.get(AccountModel, str(account.id))

        if model is None:
            raise NotFoundError(
                f"Account '{account.id}' was not found in the database during update. "
                "This should not happen — the use case should have verified existence first."
            )

        # Apply only the fields that are allowed to change.
        # current_balance is included because balance updates from future
        # transaction operations will go through this path.
        model.name = account.name
        model.account_type = account.account_type.value
        model.current_balance = account.current_balance

        self._session.flush()
        return self._to_domain(model)

    def delete(self, account_id: UUID, user_id: UUID) -> None:
        """
        Delete an account, enforcing ownership first.

        accounts.id is referenced by transactions.account_id and
        transfers.from_account_id/to_account_id, both ON DELETE RESTRICT.
        If the account still has financial history, the database refuses
        the delete with an IntegrityError, which we translate into a
        ConflictError — a 409 is the correct, meaningful response for
        "this account cannot be deleted while it still has transactions".
        """
        model = self._session.get(AccountModel, str(account_id))
        if model is None or model.user_id != str(user_id):
            return

        try:
            self._session.delete(model)
            self._session.flush()
        except IntegrityError:
            raise ConflictError(
                "This account cannot be deleted because it still has "
                "transactions or transfers linked to it. Delete or "
                "reassign them first."
            )

    # ── Private mapping methods ───────────────────────────────────────────────

    def _to_domain(self, model: AccountModel) -> Account:
        """
        Convert an ORM model row to a domain entity.

        Why convert at all? The domain entity (Account) contains business
        methods and uses pure Python types. The ORM model is a database
        mapping class. Keeping them separate lets us change either without
        touching the other.
        """
        return Account(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            name=model.name,
            account_type=AccountType(model.account_type),
            currency=model.currency,
            opening_balance=model.opening_balance,
            current_balance=model.current_balance,
            created_at=model.created_at,
        )

    def _to_model(self, account: Account) -> AccountModel:
        """
        Convert a domain entity to an ORM model for persistence.

        UUIDs are stored as strings (VARCHAR(36)) because SQLite has no
        native UUID type. The conversion is always explicit here — no
        implicit coercion happens elsewhere.

        AccountType enum values are stored as their string value (.value)
        because the database column stores a plain string, and CHECK constraints
        validate the allowed values.
        """
        return AccountModel(
            id=str(account.id),
            user_id=str(account.user_id),
            name=account.name,
            account_type=account.account_type.value,
            currency=account.currency,
            opening_balance=account.opening_balance,
            current_balance=account.current_balance,
            created_at=account.created_at,
        )
