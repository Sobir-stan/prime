from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.config import BASE_DIR
from app.db.database import get_db
from app.db import crud

router = APIRouter()

@router.get("/rating", response_class=HTMLResponse)
def rating_page():
    with open(BASE_DIR/"frontend/rating.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/get_rating")
def get_rating(db: Session = Depends(get_db)):
    top_progress = crud.get_top_progress(db, limit=10)
    result = []
    for p in top_progress:
        result.append({
            "username": p.username,
            "totalCookies": p.totalCookies,
            "cps": p.cps
        })
    return result

@router.get("/get_rank/{username}")
def get_rank(username: str, db: Session = Depends(get_db)):
    rank = crud.get_progress_rank(db, username)
    return {"rank": rank}