from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException, status, Security, Form, Response
from fastapi.security import  OAuth2PasswordRequestForm
from pydantic import BaseModel
import api.authentication as auth
import api.transactions as trx
from datetime import date
from database import Transaction

app = FastAPI()

@app.post("/token", response_model=auth.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect Username or Password")

    access_token = auth.create_access_token(data = {"sub": user.username})

    return auth.Token(access_token=access_token, token_type="jwt")

@app.post("/signup")
async def signup(
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
    ):
    auth.create_new_user(name, username, email, password)

    return Response(status_code=status.HTTP_201_CREATED)

class TransactionPost(BaseModel):
    title: str
    amount: Decimal
    transaction_date: date
    payer_id: int
    group_id: int
    breakdown: dict[int, Decimal]

class TransactionPatch(BaseModel):
    transaction_id: int
    title: str | None = None
    amount: Decimal | None = None
    transaction_date: date | None = None
    payer_id: int | None = None
    group_id: int | None = None
    breakdown: dict[int, Decimal] | None = None

@app.post("/transaction")
async def post_transaction(transaction: TransactionPost):
    trx.create_transaction(
        transaction.title,
        transaction.amount,
        transaction.transaction_date,
        transaction.payer_id,
        transaction.group_id,
        transaction.breakdown
        )

    return Response(status_code=status.HTTP_201_CREATED)

@app.patch("/transaction")
async def patch_transaction(transaction: TransactionPatch):
    trx.update_transaction(
        transaction.transaction_id,
        title = transaction.title,
        amount = transaction.amount,
        transaction_date = transaction.transaction_date,
        payer_id = transaction.payer_id,
        group_id = transaction.group_id,
        breakdown = transaction.breakdown
    )

    return Response(status_code=status.HTTP_202_ACCEPTED)

@app.get("/transaction", response_model=Transaction)
async def get_transaction(transaction_id: int):
    transaction =  trx.get_transaction(transaction_id)

    return transaction