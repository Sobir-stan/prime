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

