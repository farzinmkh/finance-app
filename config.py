"""
Application Configuration
=========================
Reads configuration from environment variables (and optionally a .env file).

Why Pydantic BaseSettings?
- It reads values from environment variables automatically.
- It validates types (e.g. DEBUG must be a bool, not the string "true").
- It raises a clear error at startup if a required variable is missing.
- All configuration is in one place — no scattered os.environ.get() calls.

Usage anywhere in the app:
    from config import settings
    print(settings.DATABASE_URL)
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic will automatically:
    - Read values from the .env file (if it exists)
    - Read values from actual environment variables (these take priority)
    - Validate and coerce types (e.g. "false" → False for booleans)
    """

    model_config = SettingsConfigDict(
        env_file=".env",             # Load from .env file if it exists
        env_file_encoding="utf-8",
        case_sensitive=False,        # DATABASE_URL and database_url both work
        extra="ignore",              # Ignore unknown variables in .env
    )

    # --- Application ---
    APP_NAME: str = "Personal Finance Manager"
    DEBUG: bool = False

    # --- Database ---
    # Default: SQLite stored in a local file in the project root
    DATABASE_URL: str = "sqlite:///./finance.db"

    # --- Security ---
    # Used later for signing JWT tokens.
    # Must be a long random string in production.
    SECRET_KEY: str = "change-me-before-production-use"

    # How long a login session lasts (in minutes). Default: 24 hours.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_default(cls, value: str) -> str:
        """
        Warn clearly if the default insecure key is used in production.

        Note: We only warn here rather than raising an error, because
        during development and testing the default key is fine.
        In production, this should be overridden via an environment variable.
        """
        if value == "change-me-before-production-use":
            import warnings
            warnings.warn(
                "SECRET_KEY is set to the default insecure value. "
                "Set a strong random key via the SECRET_KEY environment variable "
                "before deploying to production.",
                stacklevel=2,
            )
        return value

    @field_validator("DATABASE_URL")
    @classmethod
    def database_url_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL must not be empty.")
        return value


# Single shared instance used throughout the application.
# Import this object, not the Settings class, everywhere else:
#
#   from config import settings
#   db_url = settings.DATABASE_URL
#
settings = Settings()
