"""User Repository Interface and SQLAlchemy Implementation"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> User: ...
