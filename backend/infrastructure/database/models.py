"""
SQLAlchemy ORM Models
======================
All database table definitions in one file.

Table definition order matters for FK references at class-creation time.
The safe order is:
  UserModel → AccountModel → CategoryModel → TransferModel → TransactionModel

TransferModel must precede TransactionModel because TransactionModel has
a FK to transfers.id. With SQLAlchemy's DeclarativeBase, FK targets can
be referenced as strings (e.g. ForeignKey("transfers.id")), so forward
references are technically allowed — but explicit ordering avoids confusion.

ORM models vs Domain entities — the key distinction:
  Domain entity  → pure Python, contains business rules, no DB awareness
  ORM model      → SQLAlchemy class, maps to a table, no business rules
  Repository     → bridges the two (maps ORM ↔ domain entity)

Monetary fields: Numeric(19, 4, asdecimal=True) everywhere.
  asdecimal=True ensures SQLAlchemy returns Decimal, never float.
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Root base class. Alembic reads Base.metadata for schema detection."""
    pass


# ── Users ────────────────────────────────────────────────────────────────────


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    accounts: Mapped[list["AccountModel"]] = relationship(
        "AccountModel", back_populates="user", cascade="all, delete-orphan",
    )
    categories: Mapped[list["CategoryModel"]] = relationship(
        "CategoryModel", back_populates="user", cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(email)) > 0", name="ck_users_email_not_empty"),
    )


# ── Accounts ─────────────────────────────────────────────────────────────────


class AccountModel(Base):
    """
    Balance invariant (maintained by the application, never set by user input):
        current_balance = opening_balance
                        + SUM(income transactions)
                        - SUM(expense transactions)
    """
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4, asdecimal=True), nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(19, 4, asdecimal=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="accounts")

    __table_args__ = (
        CheckConstraint(
            "account_type IN ('checking', 'savings', 'credit', 'cash')",
            name="ck_accounts_account_type_valid",
        ),
        CheckConstraint("LENGTH(currency) = 3", name="ck_accounts_currency_length"),
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_accounts_name_not_empty"),
        Index("idx_accounts_user_id", "user_id"),
    )


# ── Categories ───────────────────────────────────────────────────────────────


class CategoryModel(Base):
    """
    User-owned transaction labels. category_type is immutable after creation.
    UNIQUE(user_id, name): a user cannot have two categories with the same name.
    ON DELETE SET NULL on transactions.category_id: deleting a category
    uncategorises its transactions rather than deleting them.
    """
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 'income' or 'expense' — enforced by CHECK constraint
    category_type: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="categories")

    __table_args__ = (
        CheckConstraint(
            "category_type IN ('income', 'expense')",
            name="ck_categories_type_valid",
        ),
        CheckConstraint("LENGTH(TRIM(name)) > 0", name="ck_categories_name_not_empty"),
        # One name per user. Different users can share names.
        UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
        Index("idx_categories_user_id", "user_id"),
    )


# ── Transfers ─────────────────────────────────────────────────────────────────


class TransferModel(Base):
    """
    Represents the movement of money between two accounts owned by the same user.

    A Transfer is a first-class entity. It owns exactly two Transaction rows
    (the 'legs'), identified by transactions.transfer_id = this transfer's id.

    Deletion order (enforced by the use case):
      1. Delete both transaction legs  ← must come first (FK RESTRICT)
      2. Delete this Transfer row

    Account deletion is blocked (ON DELETE RESTRICT) while a transfer references
    either account. Users must delete their transfers before deleting an account.
    """
    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    # RESTRICT: cannot delete an account that is part of a transfer
    from_account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False,
    )
    to_account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4, asdecimal=True), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transfers_amount_positive"),
        CheckConstraint(
            "from_account_id != to_account_id",
            name="ck_transfers_different_accounts",
        ),
        Index("idx_transfers_user_id", "user_id"),
        Index("idx_transfers_from_account_id", "from_account_id"),
        Index("idx_transfers_to_account_id", "to_account_id"),
    )


# ── Transactions ─────────────────────────────────────────────────────────────


class TransactionModel(Base):
    """
    A single financial event (income or expense) against one Account.

    transfer_id is nullable:
      - NULL:      a standalone income or expense transaction
      - non-NULL:  a leg of a Transfer (locked — cannot be independently
                   edited or deleted; only DeleteTransfer may remove it)

    FK on transfer_id uses RESTRICT: you cannot delete a Transfer while
    its transaction legs still exist. The DeleteTransfer use case deletes
    the legs first, then the Transfer, to satisfy this constraint.

    FK on category_id uses SET NULL: deleting a Category uncategorises
    its transactions (sets category_id to NULL) rather than deleting them.
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # RESTRICT: cannot delete an account that has transactions
    account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False,
    )
    # CASCADE: deleting a user deletes their transactions
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    # SET NULL: deleting a category uncategorises its transactions
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True,
    )
    # RESTRICT: transaction legs cannot outlive their Transfer
    transfer_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("transfers.id", ondelete="RESTRICT"), nullable=True,
    )
    # 'income' or 'expense'
    transaction_type: Mapped[str] = mapped_column(String(10), nullable=False)
    # Always positive. Direction is encoded in transaction_type.
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4, asdecimal=True), nullable=False)
    # Financial date — the day the transaction occurred, not when it was entered
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('income', 'expense')",
            name="ck_transactions_type_valid",
        ),
        CheckConstraint("amount > 0", name="ck_transactions_amount_positive"),
        # Most queries filter by (account_id, date) — composite index covers both
        Index("idx_transactions_account_date", "account_id", "date"),
        Index("idx_transactions_user_id", "user_id"),
        Index("idx_transactions_transfer_id", "transfer_id"),
        Index("idx_transactions_category_id", "category_id"),
    )


# ── Budgets ───────────────────────────────────────────────────────────────────


class BudgetModel(Base):
    """
    Maps to the 'budgets' table.

    A budget stores only the spending limit (amount). Current spending,
    remaining amount, and percentage are always computed from real
    transactions at query time — never cached here.

    UNIQUE(user_id, category_id, month, year): one budget per category
    per calendar month per user.

    ON DELETE CASCADE for both user_id and category_id:
      - Deleting a user removes all their budgets.
      - Deleting a category removes all its budgets (the category is gone,
        so tracking spending against it is meaningless).
    """

    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False,
    )
    # The spending limit for the month.
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 4, asdecimal=True), nullable=False)
    # 1–12, enforced by CHECK constraint.
    month: Mapped[int] = mapped_column(nullable=False)
    # 2000–2100, enforced by CHECK constraint.
    year: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
        CheckConstraint("month >= 1 AND month <= 12", name="ck_budgets_month_valid"),
        CheckConstraint("year >= 2000 AND year <= 2100", name="ck_budgets_year_valid"),
        # Core uniqueness rule: one budget per category per month per user.
        UniqueConstraint("user_id", "category_id", "month", "year",
                         name="uq_budgets_user_category_month_year"),
        Index("idx_budgets_user_id", "user_id"),
        Index("idx_budgets_user_month_year", "user_id", "month", "year"),
    )
