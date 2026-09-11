"""Auth Use Cases — Register and Login"""
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from domain.entities.user import User
from domain.exceptions import AuthenticationError, ConflictError, DomainValidationError
from domain.repositories.user_repository import UserRepository
from infrastructure.security.password import hash_password, verify_password


@dataclass
class RegisterUserInput:
    email: str
    password: str


@dataclass
class AuthOutput:
    user_id: str
    email: str


class RegisterUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repo = user_repository

    def execute(self, input_data: RegisterUserInput) -> AuthOutput:
        email = input_data.email.lower().strip()

        if not email or "@" not in email:
            raise DomainValidationError("A valid email address is required.")
        if len(input_data.password) < 8:
            raise DomainValidationError("Password must be at least 8 characters.")

        if self._repo.get_by_email(email) is not None:
            raise ConflictError("An account with this email already exists.")

        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hash_password(input_data.password),
            created_at=datetime.now(timezone.utc),
        )
        self._repo.save(user)
        return AuthOutput(user_id=str(user.id), email=user.email)


class LoginUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self._repo = user_repository

    def execute(self, email: str, password: str) -> AuthOutput:
        user = self._repo.get_by_email(email.lower().strip())
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        return AuthOutput(user_id=str(user.id), email=user.email)
