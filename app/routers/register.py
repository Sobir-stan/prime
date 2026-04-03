from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.config import BASE_DIR
from app.db.database import get_db
from app.schemas import New_user
from app.db import crud

router = APIRouter()

def check_username(username, email, db: Session):
    if crud.get_user_by_username(db, username):
        return f"{username} nomli foydalanuvchi mavjud"
    if crud.get_user_by_email(db, email):
        return f"{email} ishlatilgan email"
    return None

@router.get("/register", response_class=HTMLResponse)
def register_page():
    with open(BASE_DIR/"frontend/register.html", "r", encoding="utf-8") as f:
        return f.read()

@router.post("/register")
def register_user(user: New_user, db:Session = Depends(get_db)):
    error = check_username(user.username, user.email, db)
    if error:
        raise HTTPException(status_code=400, detail=error)
    try:
        crud.create_user(user, db)
        return {"msg": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
