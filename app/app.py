from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from pydantic import BaseModel, Field
from pandas import DataFrame
import csv
import json


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "users.csv"


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
    if CSV_PATH.exists():
        try:
            with open(CSV_PATH, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing = row.get("username")
                    if existing and existing.strip().lower() == user.username.strip().lower():
                        raise HTTPException(status_code=400, detail="Username already exists")
        except HTTPException:
            raise
        except Exception as e:
            print(e)

    data = user.dict()
    df = DataFrame([data])
    exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", encoding="utf-8", newline='') as f:
        df.to_csv(f, header=not exists, index=False)
    print(user)
    return user


@app.get("/users")
def get_users():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        users = list(reader)
    return {"users":users}