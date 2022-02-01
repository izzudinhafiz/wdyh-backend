from sqlmodel import Field, SQLModel, Relationship, Session, select
from datetime import date
from sqlalchemy import Column, Date
from sqlalchemy.dialects import postgresql as psql
from typing import TYPE_CHECKING, Any, Dict, List
from .link_model import UserTransactionLink
from .types import Money
from ..errors import TransactionDoesNotExistError


if TYPE_CHECKING:
   from .users import User
   from .groups import Group

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    amount: Money
    transaction_date: date = Field(sa_column=Column(Date()), nullable=False)
    category: str = Field(default="General")
    sub_category: str = Field(default="Others")
    notes: str | None = Field(default=None)
    details: Dict[str, Any] | None = Field(default=None, sa_column=Column(psql.JSONB()))

    # Foreign Attributes
    group_id: int | None = Field(default=None, foreign_key="group.id", nullable=False)
    group: "Group" = Relationship(back_populates="transactions")
    payer_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    payer: "User" = Relationship(back_populates="as_payer")
    payees: List["User"] = Relationship(back_populates="as_payee", link_model=UserTransactionLink, sa_relationship_kwargs={"viewonly": True})
    transaction_link: List["UserTransactionLink"] = Relationship(back_populates="transaction",  sa_relationship_kwargs={"overlaps": "as_payee,payees"})

    @classmethod
    def get_by_id(cls, transaction_id: int, session: Session):
        transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
        if not transaction:
            raise TransactionDoesNotExistError(f"Transaction with id: {transaction_id} does not exist")
        return transaction