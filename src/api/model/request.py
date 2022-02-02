from pydantic import BaseModel
from decimal import Decimal
from typing import Any
from datetime import date
from database.models.transactions import TransactionBase


class GroupPost(BaseModel):
    name: str
    type: str = "General"
    image: bytes | None = None

class Breakdown(BaseModel):
    payer: int
    payee: int
    amount: Decimal
    item_detail: dict[str, Any]

class TransactionPost(TransactionBase):
    group_id: int
    breakdowns: list[Breakdown]

class TransactionPatch(BaseModel):
    transaction_id: int
    title: str | None = None
    amount: Decimal | None = None
    transaction_date: date | None = None
    payer_id: int | None = None
    group_id: int | None = None
    breakdown: dict[int, Breakdown] | None = None