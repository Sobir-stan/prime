from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"


@app.get("/", response_class=HTMLResponse)
def home():
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/send")
def send_info():
    return {"message": "Use POST to send data to this endpoint"}


@app.post("/send")
def receive_data(request: Request):
    data = request.json()

    return {
        "received_first": data.get("first"),
        "received_second": data.get("second")
    }
