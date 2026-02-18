from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path

from starlette.staticfiles import StaticFiles

from app.schemas import Body_test, New_user
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
app.mount("/static/scripts", StaticFiles(directory=BASE_DIR/"frontend/scripts"), name="static")


# @app.get("/", response_class=HTMLResponse)
# def home():
#     with open(INDEX_FILE, "r", encoding="utf-8") as f:
#         return f.read()
#
# class userLoginShcemema(BaseModel):
#     username: str
#     age: int = Field(ge = 0, le=100)

@app.get("/product/{id}")
def login(id : int):
    print(id)
    return {"id": id}


@app.get("/product/")
def login(param : int):
    print(param)
    return {"param": param}

@app.post("/body_test")
def body_test(data : Body_test):
    print(data)
    return data

@app.post("/send")
def get_entered_data(text : dict):
    print(text)
    return {"text": text}

@app.get("/register", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/register")
def register_user(user: New_user):
    print(user.username, user.email, user.password)
    return {"msg": "ok"}

