from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict
from sqlmodel import Field, Relationship, SQLModel, Session, select
from sqlalchemy import Column, DateTime
from datetime import datetime
from sqlalchemy.dialects import postgresql as psql
from ..types import Money, SessionData
from ...errors import JournalDoesNotExistError

if TYPE_CHECKING:
    from ..transactions import Transaction
    from ..users import User

class JournalBase(SQLModel):
    transaction_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    amount: Money
    item_detail: Dict[str, Any] = Field(default=None, sa_column=Column(psql.JSONB()))

class Journal(JournalBase, table=True):
    created_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))
    updated_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow))
    payer_id: int = Field(foreign_key="user.id", primary_key=True)
    payee_id: int = Field(foreign_key="user.id", primary_key=True)
    transaction: "Transaction" = Relationship(back_populates="journals")
    payer: "User" = Relationship(back_populates="as_payer", sa_relationship_kwargs={"primaryjoin": "Journal.payer_id==User.id"})
    payee: "User" = Relationship(back_populates="as_payee", sa_relationship_kwargs={"primaryjoin": "Journal.payee_id==User.id"})

    @classmethod
    def get_by_id(cls, transaction_id: int, user_id: int, session: Session):
        transaction = session.exec(select(Journal).where(Journal.transaction_id == transaction_id, Journal.payer_id == user_id)).first()
        if not transaction:
            raise JournalDoesNotExistError(f"Transaction with id: {transaction_id} does not exist")
        return transaction

    @classmethod
    def get_user_balance(cls, session: SessionData) -> Decimal:
        payer_journals = session.conn.exec(select(Journal).where(Journal.payer == session.user)).all()
        payee_journals = session.conn.exec(select(Journal).where(Journal.payee == session.user)).all()

        lent = sum([x.amount for x in payer_journals])
        borrowed = sum([x.amount for x in payee_journals])

        return Decimal(lent - borrowed)