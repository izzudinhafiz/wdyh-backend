from dotenv import dotenv_values
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from jose import jwt
from passlib.context import CryptContext
from database import database, User
from database.errors import UserDoesNotExistError
from database.models.types import SessionData
from sqlmodel import Session

DOTENV_CONFIGS = dotenv_values("../.env")
SECRET_KEY = DOTENV_CONFIGS["HASH_SECRET_KEY"]
ALGORITHM = "HS256"
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str

    def to_jwt(self):
        """Converts data within to JWT format"""
        return jwt.encode({"sub": self.username}, SECRET_KEY, ALGORITHM)

    @classmethod
    def from_jwt(cls, data: str):
        payload = jwt.decode(data, SECRET_KEY, ALGORITHM)
        return cls(username=payload["sub"])


# class SessionData:
#     def __init__(self, conn: Session, user: User):
#         self.conn = conn
#         self.user = user

def verify_hashed_password(plain_password, hashed_password) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def hash_password(password) -> str:
    return PWD_CONTEXT.hash(password)

def create_new_user(name: str, username: str, email: str, password: str) -> User:
    """Creates a new user in the database"""
    try:
        with Session(database) as session:
            user = User(name=name, email=email, username=username, password=hash_password(password))
            session.add(user)
            session.commit()
            session.refresh(user)

        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

def authenticate_user(username: str, password: str) -> User:
    """
    Verifies if the user has the correct login credentials

    Raises a HTTPException if user is invalid
    """
    credentials_exception = HTTPException(status_code=401, detail="Incorrect Username or Password")
    with Session(database) as session:
        try:
            user = User.get_by_username(username, session)
        except UserDoesNotExistError:
            raise credentials_exception

    if not verify_hashed_password(password, user.password):
        raise credentials_exception

    return user

async def session_data(token: str = Depends(OAUTH2_SCHEME)):
    """
    Returns session data that has a connection and a user attached.

    Will raise a HTTP Exception if:

    (1) JWT token is invalid
    (2) user does not exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = TokenData.from_jwt(token)
    except Exception as e:
        raise credentials_exception

    with Session(database) as session:
        try:
            user = User.get_by_username(token_data.username, session)
        except UserDoesNotExistError:
            raise credentials_exception

        yield SessionData(conn=session, user=user)



