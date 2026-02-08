from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from pydantic import BaseModel, Field, StrictStr, EmailStr


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent


@app.get("/product/{id}")
def login(id : int):
    print(id)
    return {"id": id}


@app.get("/product/")
def login(param : int):
    print(param)
    return {"param": param}


@app.get("/test", response_class=HTMLResponse)
def test_display_html():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1)
    email: str


@app.post("/send")
def receive_user(user: UserSchema):
    print(user)
    return user
