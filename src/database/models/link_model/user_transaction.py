from sqlmodel import Field, Relationship, SQLModel, Session, select
from ..types import Money
from typing import TYPE_CHECKING
from ...errors import UserTransactionLinkDoesNotExistError

if TYPE_CHECKING:
    from ..transactions import Transaction
    from ..users import User

class UserTransactionLink(SQLModel, table=True):
    transaction_id: int | None = Field(default=None, foreign_key="transaction.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    amount: Money
    transaction: "Transaction" = Relationship(back_populates="transaction_link")
    user: "User" = Relationship(back_populates="transaction_links")

    @classmethod
    def get_by_id(cls, transaction_id: int, user_id: int, session: Session):
        transaction = session.exec(select(UserTransactionLink).where(UserTransactionLink.transaction_id == transaction_id, UserTransactionLink.user_id == user_id)).first()
        if not transaction:
            raise UserTransactionLinkDoesNotExistError(f"Transaction with id: {transaction_id} does not exist")
        return transaction