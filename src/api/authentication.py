from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import dotenv_values
from database import database, User
from sqlmodel import Session, select

dotenv_configs = dotenv_values("../.env")

SECRET_KEY = dotenv_configs["HASH_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_hashed_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_new_user(name: str, username: str, email: str, password: str) -> User:
    try:
        with Session(database) as session:
            user = User(name=name, email=email, username=username, password=hash_password(password))
            session.add(user)
            session.commit()
            session.refresh(user)

        return user
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

def get_user(username: str | None) -> User | None:
    if username is None:
        return

    with Session(database) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        return user

def authenticate_user(username: str, password: str) -> User:
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect Username or Password")
    if not verify_hashed_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect Username or Password")

    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    token_data = TokenData(username=username)
    user = get_user(username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


