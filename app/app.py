from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from pydantic import BaseModel, Field
from pandas import DataFrame
from typing import Optional
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
    next_id = 0
    if CSV_PATH.exists():
        try:
            with open(CSV_PATH, "r", encoding="utf-8", newline='') as f:
                reader = csv.DictReader(f)
                max_id = 0
                for row in reader:
                    try:
                        rid = int(row.get('id') or 0)
                        if rid > max_id:
                            max_id = rid
                    except Exception:
                        continue
                next_id = max_id + 1
        except Exception as e:
            print(e)
            next_id = 1

    data['id'] = next_id
    df = DataFrame([data])
    exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", encoding="utf-8", newline='') as f:
        df.to_csv(f, header=not exists, index=False)
    print(user)
    return user


@app.get("/users")
def get_users(name: Optional[str] = None):
    if name:
        return _find_user(name)

    if not CSV_PATH.exists():
        return {"users": []}

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        users = list(reader)
    return {"users": users}


def _find_user(name: str):
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="Users file not found")

    target = name.strip().lower()
    if not target:
        raise HTTPException(status_code=400, detail="Missing 'name' parameter")

    with open(CSV_PATH, "r", encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = (row.get("username") or "").strip()
            if username and username.lower() == target:
                return {
                    "user": {
                        "username": row.get("username"),
                        "password": row.get("password"),
                        "email": row.get("email"),
                        "id": row.get("id")
                    }
                }
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{name}")
def get_user(name: str):
    return _find_user(name)
