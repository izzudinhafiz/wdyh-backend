from pydantic import BaseModel
from decimal import Decimal

class Overview(BaseModel):
    balance: Decimal
    sessions: int

class IDResponse(BaseModel):
    id: int
