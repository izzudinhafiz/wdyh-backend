from pydantic import BaseModel
from decimal import Decimal

class Overview(BaseModel):
    balance: Decimal
    sessions: int

class IDResponse(BaseModel):
    id: int

class UserResponse(BaseModel):
    id: int
    name: str
    push_on: bool
    email_on: bool

class PayStructResponse(BaseModel):
    debtor_id: int
    debtee_id: int
    amount: Decimal

    def __str__(self) -> str:
        return f"{self.debtee_id} -> {self.amount} -> {self.debtor_id}"