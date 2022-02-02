from sqlmodel import Field, Relationship, SQLModel, select
from datetime import datetime
from sqlalchemy import Column, DateTime, LargeBinary
from typing import TYPE_CHECKING, List
from .link_model import UserGroupLink
from ..errors import GroupDoesNotExistError
from .types import SessionData


if TYPE_CHECKING:
    from .users import User
    from .transactions import Transaction
    from api.model.request import GroupPost

class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    image: bytes = Field(default= None, sa_column=Column(LargeBinary()))
    type: str = Field(default="General")
    created_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))
    deleted_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), default=None))
    deleted: bool = False

    # Foreign Attributes
    users: List["User"] = Relationship(back_populates="groups", link_model=UserGroupLink)
    transactions: List["Transaction"] = Relationship(back_populates="group")

    @classmethod
    def get_by_id(cls, group_id: int, session: SessionData):
        group = session.conn.exec(select(Group).where(Group.id == group_id)).first()
        if not group:
            raise GroupDoesNotExistError(f"Group with id {group_id} does not exist")
        return group

    @classmethod
    def create_group(cls, data: "GroupPost", session: SessionData) -> int:
        group = Group(name=data.name, type=data.type)
        if data.image:
            group.image = data.image

        session.conn.add(group)
        session.user.groups.append(group)
        session.conn.commit()
        session.conn.refresh(group)
        return group.id # type: ignore

    @classmethod
    def get_users(cls, group_id: int, session: SessionData):
        group = cls.get_by_id(group_id, session)
        return group.users