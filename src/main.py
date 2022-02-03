from fastapi import FastAPI, Depends, status, Security, Form, Response
from fastapi.security import  OAuth2PasswordRequestForm
from api.model.response import *
from api.model.request import *
from database import Transaction, Group, Journal
from database.models.types import SessionData
import api.authentication as auth

app = FastAPI()

@app.post("/token", response_model=auth.Token, tags=["authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    token_data = auth.TokenData(username=user.username)
    return auth.Token(access_token=token_data.to_jwt())

@app.post("/signup", tags=["authentication"])
async def signup(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
    ):
    auth.create_new_user(name, username, email, password)

    return Response(status_code=status.HTTP_201_CREATED)



@app.post("/transaction", tags=["transaction"], response_model=IDResponse)
async def create_transaction(transaction: TransactionPost, session: SessionData = Security(auth.session_data)):
    transaction_id = Transaction.create_transaction(transaction, session)
    return IDResponse(id=transaction_id)

@app.get("/transaction", response_model=Transaction, tags=["transaction"])
async def get_transaction(transaction_id: int, session: SessionData = Security(auth.session_data)):
    return Transaction.get_by_id(transaction_id, session)

@app.get("/transaction/group_transactions", response_model=list[Transaction], tags=["transaction"])
async def get_group_transactions(group_id: int, session: SessionData = Security(auth.session_data)):
    return Transaction.get_group_transactions(group_id, session)

@app.get("/transaction/group_sessions", response_model=list[Transaction], tags=["transaction"])
async def get_group_sessions(group_id: int, session: SessionData = Security(auth.session_data)):
    return Transaction.get_group_sessions(group_id, session)

@app.get("/transaction/simplify_debt", response_model=list[PayStructResponse], tags=["transaction"])
async def simplify_debts(session: SessionData = Security(auth.session_data)):
    transactions = Transaction.get_closed_transactions(1, session)
    return Journal.get_users_debt([x.id for x in transactions], session) # type: ignore



@app.post("/group/create", tags=["group"], response_model=IDResponse)
async def create_group(data: GroupPost, session: SessionData = Security(auth.session_data)):
    group_id = Group.create_group(data, session)
    return IDResponse(id=group_id)

@app.post("/group/{group_id}/adduser", tags=["group"])
async def add_user_to_group(group_id: int, session: SessionData = Security(auth.session_data)):
    group = Group.get_by_id(group_id, session)
    session.user.groups.append(group)
    session.conn.commit()
    return Response(status_code=status.HTTP_200_OK)

@app.get("/group/{group_id}/users", response_model=list[UserResponse], tags=["group"])
async def get_users(group_id: int, session: SessionData = Security(auth.session_data)):
    return Group.get_users(group_id, session)




@app.get("/user/overview", response_model=Overview, tags=["user"])
async def get_user_overview(session: SessionData = Security(auth.session_data)):
    balance = Journal.get_user_balance(session)
    num_sessions = len(Transaction.get_active_session(session))

    return Overview(balance=balance, sessions=num_sessions)

@app.get("/user/active_sessions", response_model=list[Transaction], tags=["user"])
async def get_user_active_sessions(session: SessionData = Security(auth.session_data)):
    return Transaction.get_active_session(session)