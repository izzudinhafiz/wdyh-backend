from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel, Session, select
from sqlalchemy import Column, DateTime
from datetime import datetime
from sqlalchemy.dialects import postgresql as psql
from api.model.response import PayStructResponse
from ..types import Money, SessionData
from ...errors import JournalDoesNotExistError

if TYPE_CHECKING:
    from ..transactions import Transaction
    from ..users import User

class Balance(BaseModel):
    user_id: int
    amount: Decimal

    def __str__(self) -> str:
        return f"{self.user_id}: {self.amount}"

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

    @classmethod
    def get_users_debt(cls, transaction_ids: list[int], session: SessionData):
        journals = session.conn.exec(select(Journal).where(Journal.transaction_id.in_(transaction_ids))).all() # type: ignore

        members = [x.payer_id for x in journals]
        members = members + [x.payee_id for x in journals]
        members = list(set(members))

        balance: list[Balance] = []
        for user_id in members:
            debits = sum([x.amount for x in journals if x.payer_id == user_id], start=Decimal(0))
            credits = sum([x.amount for x in journals if x.payee_id == user_id], start=Decimal(0))
            balance.append(Balance(user_id=user_id, amount=(debits-credits)))

        return simplify(balance)

def simplify(balance: list[Balance]):
    pay_tree = []
    total = sum([x.amount for x in balance], start=Decimal(0))

    if total != 0:
        raise ValueError("Mismatched balance, cannot simplify")

    while True:
        balance = list(sorted(balance, key=lambda x: x.amount, reverse=True))
        if len(balance) == 0:
            break
        debit = balance[0]
        credit = balance[-1]

        if debit.amount >= abs(credit.amount):
            difference = debit.amount + credit.amount
            pay_tree.append(PayStructResponse(debtor_id=debit.user_id, debtee_id=credit.user_id, amount=abs(credit.amount)))
            balance.pop()
            balance[0].amount = difference
            if difference == Decimal(0):
                balance.pop(0)
        else:
            difference = debit.amount + credit.amount
            pay_tree.append(PayStructResponse(debtor_id=debit.user_id, debtee_id=credit.user_id, amount=debit.amount))
            balance.pop(0)
            balance[-1].amount = difference

    return pay_tree