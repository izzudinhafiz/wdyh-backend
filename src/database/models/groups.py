from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy import Column, DateTime, String, LargeBinary
from typing import TYPE_CHECKING, Literal, List
from .link_model import UserGroupLink

# GroupType = Literal["General", "Work", "Personal", "Friends"]

if TYPE_CHECKING:
   from .users import User
   from .transactions import Transaction

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