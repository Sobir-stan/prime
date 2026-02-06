from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.schemas import Body_test

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent


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


@app.get("/test", response_class=HTMLResponse)
def test_display_html():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
            return f.read()

@app.post("/send")
def get_entered_data(text : dict):
    print(text)
    return {"text": text}