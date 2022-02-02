from sqlmodel import Field, SQLModel, Relationship, Session, select
from datetime import date
from sqlalchemy import Column, Date, DateTime
from sqlalchemy.dialects import postgresql as psql
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List
from .link_model import Journal
from .types import Money, SessionData
from ..errors import TransactionDoesNotExistError

if TYPE_CHECKING:
    from .groups import Group
    from api.model.request import TransactionPost


class TransactionBase(SQLModel):
    description: str
    amount: Money
    transaction_date: date = Field(sa_column=Column(Date()), nullable=False, index=True)
    category: str = Field(default="General")
    sub_category: str = Field(default="Others")
    notes: str | None = Field(default=None)
    details: Dict[str, Any] | None = Field(default=None, sa_column=Column(psql.JSONB()))
    is_session: bool = Field(default=False)
    is_session_closed: bool = Field(default=False)
    is_itemized: bool = Field(default=False)


class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(default=None, foreign_key="group.id", nullable=False, index=True)
    created_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), default=datetime.utcnow))
    updated_at: datetime = Field(default=None, sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow, default=datetime.utcnow))

    # Foreign Attributes
    group: "Group" = Relationship(back_populates="transactions")
    journals: List[Journal] = Relationship(back_populates="transaction")

    @classmethod
    def get_by_id(cls, transaction_id: int, session: SessionData):
        transaction = session.conn.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
        if not transaction:
            raise TransactionDoesNotExistError(f"Transaction with id: {transaction_id} does not exist")
        return transaction

    @classmethod
    def get_group_transactions(cls, group_id: int, session: SessionData):
        return session.conn.exec(select(Transaction).where(Transaction.group_id == group_id)).all()

    @classmethod
    def get_active_session(cls, session: "SessionData"):
        groups = session.user.groups
        groups_id = [x.id for x in groups]
        trx_sessions = session.conn.exec(select(Transaction).where(Transaction.group_id.in_(groups_id), Transaction.is_session == True, Transaction.is_session_closed == False)).all() # type: ignore

        return trx_sessions

    @classmethod
    def get_group_sessions(cls, group_id: int, session: SessionData):
        return session.conn.exec(select(Transaction).where(Transaction.group_id==group_id, Transaction.is_session==True, Transaction.is_session_closed==False)).all()

    @classmethod
    def create_transaction(cls, data: "TransactionPost", session: SessionData) -> int:
        breakdown_total = sum([x.amount for x in data.breakdowns])
        if data.amount != breakdown_total:
            raise ValueError(f"Mismatch totals. Total amount should be {data.amount}. Breakdown amount is {breakdown_total}")

        transaction = Transaction(description=data.description,
                                amount=data.amount,
                                transaction_date=data.transaction_date,
                                category=data.category,
                                sub_category=data.sub_category,
                                notes=data.notes,
                                details=data.details,
                                is_session=data.is_session,
                                is_session_closed=data.is_session_closed,
                                is_itemized=data.is_itemized,
                                group_id=data.group_id,
                                )

        transaction_details = []
        for breakdown in data.breakdowns:
            transaction_details.append(Journal(
                transaction=transaction,
                payer_id=breakdown.payer,
                payee_id=breakdown.payee,
                amount=breakdown.amount,
                item_detail=breakdown.item_detail,
                ))

        session.conn.add(transaction)
        session.conn.commit()
        session.conn.refresh(transaction)

        return transaction.id # type: ignore