"""
Domain Exceptions
=================
All exceptions that represent business rule violations are defined here.

Why a dedicated exceptions module?
- The presentation layer catches these and maps them to HTTP status codes.
- The domain layer raises them without knowing anything about HTTP.
- Having them in one place makes the mapping clear and maintainable.

Dependency rule: This file imports NOTHING from outside the standard library.
It must not import FastAPI, SQLAlchemy, or any other framework.
"""


class FinanceAppError(Exception):
    """
    Base exception for all domain-level errors.

    Catch this if you want to handle any application error.
    Catch a subclass if you want to handle a specific case.
    """
    pass


class NotFoundError(FinanceAppError):
    """
    Raised when a requested resource does not exist.

    Examples:
    - Requesting account with an ID that does not belong to the user.
    - Requesting a transaction that was already deleted.

    Maps to HTTP 404.
    """
    pass


class AuthorizationError(FinanceAppError):
    """
    Raised when a user attempts to access or modify a resource
    they do not own.

    This is distinct from authentication (proving who you are).
    Authorization means: you are authenticated, but not permitted.

    Maps to HTTP 403.
    """
    pass


class DomainValidationError(FinanceAppError):
    """
    Raised when an operation violates a business rule.

    Examples:
    - Transferring money between the same account.
    - Setting a transaction amount to zero or negative.
    - Assigning an expense category to an income transaction.

    Maps to HTTP 422.
    """
    pass


class ConflictError(FinanceAppError):
    """
    Raised when an operation would create a conflicting state.

    Examples:
    - Creating a category with a name that already exists for this user.
    - Creating a budget for a category/month combination that already has one.

    Maps to HTTP 409.
    """
    pass


class TransactionLockedError(FinanceAppError):
    """
    Raised when a transaction cannot be edited or deleted independently
    because it is part of a transfer.

    Transfers are modified as a unit — you cannot delete just one leg
    of a transfer without corrupting the financial record.

    Maps to HTTP 422.
    """
    pass


class AuthenticationError(FinanceAppError):
    """
    Raised when an authentication operation fails.

    Distinct from AuthorizationError (which is about permission to access a
    specific resource). AuthenticationError means the identity cannot be
    established at all — invalid credentials, expired token, invalid token.

    Maps to HTTP 401 Unauthorized.
    """
    pass
