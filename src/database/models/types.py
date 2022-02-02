from pydantic import condecimal, BaseModel
from typing import TYPE_CHECKING
from sqlmodel import Session

if TYPE_CHECKING:
    from .users import User

Money = condecimal(max_digits=10, decimal_places=2)

class SessionData:
    def __init__(self, user: "User", conn: Session):
        self.user = user
        self.conn = conn
