"""SQLAlchemy User Repository"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._session.get(UserModel, str(user_id))
        return self._to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def save(self, user: User) -> User:
        model = UserModel(
            id=str(user.id),
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
        self._session.add(model)
        self._session.flush()
        return user

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=UUID(model.id),
            email=model.email,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )
