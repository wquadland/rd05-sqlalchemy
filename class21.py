"""Notes for Class 21: Bringing Pydantic, SqlAlchemy, and Services together."""

# Be sure to run: `python3 -m pip install -r requirements.txt`

from typing import Self, Type


# ========================
# Pydantic

from pydantic import BaseModel, validator

class User(BaseModel):
    pid: int
    first_name: str
    last_name: str

    @validator('pid')
    def pid_must_be_9_digits(cls, value: int):
        # TODO: Raise ValueError if pid is not 9 digits
        return value


# ========================
# SqlAlchemy

from sqlalchemy import create_engine, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
engine = create_engine('sqlite+pysqlite:///:memory:', echo=True)
session_factory = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    ...


class UserEntity(Base):
    __tablename__ = "users"

    pid: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)

    @classmethod
    def from_model(cls: Type[Self], user: User) -> Self:
        return UserEntity(pid=user.pid, first_name=user.first_name, last_name=user.last_name)

    def to_model(self) -> User:
        return User(pid=self.pid, first_name=self.first_name, last_name=self.last_name)


Base.metadata.create_all(engine)


# =========================
# Service / "Business Logic"

class UserService:
    _session: Session

    def __init__(self, session: Session):
        self._session = session

    def register(self, user: User) -> User:
        user_entity: UserEntity = UserEntity.from_model(user)
        self._session.add(user_entity)
        self._session.commit()
        return user_entity.to_model()

    def get(self, pid: int) -> User:
        user = self._session.get(UserEntity, pid)
        if user:
            return user.to_model()
        else:
            raise ValueError(f"No user found with PID: {pid}")


# =========================
# Demo
# 1. Construct a User
# 2. Construct a UserService(session_factory())
# 3. Register your User object using the service
# 4. Use the get method of your service to fetch the user from database