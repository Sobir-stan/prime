from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.config import BASE_DIR, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.database import get_db
from app.db import crud
from app.schemas import Login_user, TelegramAuth
from app.core.security import pwd_context, create_access_token, get_current_user_from_cookie

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
    existing_user_with_tg_id = crud.get_user_by_telegram_id(db, data.telegram_id)
    print("123")
    if existing_user_with_tg_id:
        existing_user_with_tg_id.telegram_id = None
        db.commit()

    user = crud.get_user_by_username(db, data.username)
    if not user:
        user = crud.create_telegram_user(db, data.telegram_id)
    else:
        user.telegram_id = data.telegram_id
        db.commit()

    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)

    return {"login": "success", "username": user.username, "token": access_token}

@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    response.delete_cookie("access_token", httponly=True, samesite="none", secure=True)
    
    try:
        current_user = get_current_user_from_cookie(request)
        user = crud.get_user_by_username(db, current_user)
        if user:
            user.telegram_id = None
            db.commit()
    except:
        pass

    return {"msg": "logout successful"}

@router.get("/check_admin")
def check_admin(request: Request, db: Session = Depends(get_db)):
    """Admin tekshirish"""
    try:
        username = get_current_user_from_cookie(request)
        user = crud.get_user_by_username(db, username)
        if user and user.is_admin:
            return {"is_admin": True}
        return {"is_admin": False}
    except:
        raise HTTPException(status_code=401, detail="Sizga ruxsat yo'q")

@router.get("/check_telegram_user/{telegram_id}")
def check_telegram_user(telegram_id: int, db: Session = Depends(get_db)):
    """Telegram ID bilan ro'yxatdan o'tgan foydalanuvchini tekshirish"""
    user = crud.get_user_by_telegram_id(db, telegram_id)
    if user:
        return {"exists": True, "username": user.username}
    return {"exists": False}
