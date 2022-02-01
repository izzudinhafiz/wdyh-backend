from fastapi import FastAPI, Depends, HTTPException, status, Security, Form
from fastapi.security import  OAuth2PasswordRequestForm
from database import User
import api.authentication as auth

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

    return status.HTTP_201_CREATED


@app.get("/get_user")
def user_endpoint(current_user: User = Security(auth.get_current_user)):
    return {"username": current_user.username}