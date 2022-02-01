from sqlmodel import Field, Relationship, SQLModel
from ..types import Money
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..transactions import Transaction
    from ..users import User

class UserTransactionLink(SQLModel, table=True):
    transaction_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    amount: Money
    transaction: "Transaction" = Relationship(back_populates="transaction_link")
    user: "User" = Relationship(back_populates="transaction_links")