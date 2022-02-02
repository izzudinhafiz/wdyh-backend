from sqlmodel import Field, SQLModel, Relationship, Session, select
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from typing import TYPE_CHECKING, List
from .link_model import UserGroupLink, Journal
from ..errors import UserDoesNotExistError

if TYPE_CHECKING:
    from .groups import Group
    from .transactions import Transaction

class UserBase(SQLModel):
    name: str
    email: str = Field(sa_column=Column(String, unique=True, nullable=False))
    username: str = Field(sa_column=Column(String, unique=True, nullable=False))
    password: str
    created_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))
    updated_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow))
    last_active_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow))
    push_on: bool = False
    email_on: bool = False

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Foreign Attributes
    groups: List["Group"] = Relationship(back_populates="users", link_model=UserGroupLink)
    as_payer: List["Journal"] = Relationship(back_populates="payer", sa_relationship_kwargs={"primaryjoin": "Journal.payer_id==User.id", "lazy": "joined"})
    as_payee: List["Journal"] = Relationship(back_populates="payee", sa_relationship_kwargs={"primaryjoin": "Journal.payee_id==User.id", "lazy": "joined"})

    @classmethod
    def get_by_id(cls, user_id: int, session: Session):
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise UserDoesNotExistError(f"User with id: {user_id} does not exist")

        return user

    @classmethod
    def get_by_ids(cls, user_ids: list[int], session: Session):
        users = session.exec(select(User).where(User.id.in_(user_ids))).all() # type: ignore
        missing_user = [x for x in user_ids if x not in [y.id for y in users]]
        if missing_user:
            raise UserDoesNotExistError(f"User with id(s): {missing_user} does not exist")

        return users

    @classmethod
    def get_by_username(cls, username: str, session: Session):
        user = session.exec(select(User).where(User.username == username)).first()

        if not user:
            raise UserDoesNotExistError(f"User with username: {username} does not exist")

        return user