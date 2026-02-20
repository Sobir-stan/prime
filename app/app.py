from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
from starlette.staticfiles import StaticFiles
from app.schemas import Body_test, New_user
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()
app.mount("/static/scripts", StaticFiles(directory=BASE_DIR/"frontend/scripts"), name="static")


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

def get_csv_path():
    return BASE_DIR/"users.csv"

def ensure_csv_exist():
    csv_path = get_csv_path()

    if not csv_path.exists():
        df = pd.DataFrame(columns=("username", "email", "password"))
        df.index.name= "id"
        df.to_csv(csv_path, index=True)
        return df
    else:
        return pd.read_csv(csv_path, index_col="id")

def save_to_csv(user):
    df = ensure_csv_exist()
    csv_path = get_csv_path()

    new_user_df = pd.DataFrame([user.model_dump()])
    updated_df = pd.concat([df, new_user_df],ignore_index=True)
    updated_df.index.name = "id"

    updated_df.to_csv(csv_path,index=True )

@app.get("/register", response_class=HTMLResponse)
def register_user():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/register")
def register_user(user: New_user):
    save_to_csv(user)

    print(user.username, user.email, user.password)
    return {"msg": "ok"}

