"""
Global Exception Handlers
==========================
Maps domain-level exceptions to HTTP responses with consistent JSON format.

Why this approach?
------------------
Without these handlers, unhandled exceptions would either:
- Return FastAPI's default error format (inconsistent with our API)
- Expose internal details like stack traces or database errors (security risk)

With these handlers:
- Every domain exception becomes a predictable, documented HTTP response.
- The domain layer never imports from FastAPI — it just raises its own exceptions.
- The presentation layer handles the HTTP translation in one place.

Error response format (consistent across all endpoints):
    {
        "error": "ERROR_CODE_IN_CAPS",
        "message": "Human-readable description."
    }

HTTP status codes used:
    404 Not Found         → NotFoundError
    403 Forbidden         → AuthorizationError
    409 Conflict          → ConflictError
    422 Unprocessable     → DomainValidationError, TransactionLockedError
    500 Internal Server   → Any unhandled FinanceAppError (catch-all)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainValidationError,
    FinanceAppError,
    NotFoundError,
    TransactionLockedError,
)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all domain exception handlers with the FastAPI application.

    Called once in main.py when the application is created.
    """

    @app.exception_handler(AuthenticationError)
    async def authentication_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": "UNAUTHENTICATED", "message": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "NOT_FOUND", "message": str(exc)},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "FORBIDDEN", "message": str(exc)},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": "CONFLICT", "message": str(exc)},
        )

    @app.exception_handler(DomainValidationError)
    async def validation_handler(request: Request, exc: DomainValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "VALIDATION_ERROR", "message": str(exc)},
        )

    @app.exception_handler(TransactionLockedError)
    async def transaction_locked_handler(
        request: Request, exc: TransactionLockedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "TRANSACTION_LOCKED", "message": str(exc)},
        )

    @app.exception_handler(FinanceAppError)
    async def generic_finance_error_handler(
        request: Request, exc: FinanceAppError
    ) -> JSONResponse:
        """
        Catch-all for any domain error not handled by a more specific handler above.

        We return a generic message rather than str(exc) here to avoid accidentally
        leaking internal details for errors we did not explicitly plan for.
        """
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
            },
        )
