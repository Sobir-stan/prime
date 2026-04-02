from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import BASE_DIR, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.database import get_db
from app.db import crud
from app.schemas import Login_user, TelegramAuth
from app.core.security import pwd_context, create_access_token

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def login_page():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()

@router.post("/")
def login(user: Login_user, response: Response, db: Session = Depends(get_db)):
    row = crud.get_user_by_username(db, user.username)

    if not row:
        raise HTTPException(status_code=404, detail="foydalanuvchi mavjud emas")
    if not pwd_context.verify(user.password, str(row.password)):
        raise HTTPException(status_code=401, detail="parol to'g'ri emas")

    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)

    return {"login": "success", "username": user.username, "token": access_token}

@router.post("/tg_login")
def tg_login(data: TelegramAuth, response: Response, db: Session = Depends(get_db)):
    user = crud.get_user_by_telegram_id(db, data.telegram_id)
    if not user:
        user = crud.create_telegram_user(db, data.telegram_id)

    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)

    return {"login": "success", "username": user.username, "token": access_token}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", httponly=True, samesite="none", secure=True)
    return {"msg": "logout successful"}
