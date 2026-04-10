# Ushbu fayl login (tizimga kirish) va tizimdan chiqish (logout) marshrutlarini o'z ichiga oladi.
# Telegram orqali kirish (tg_login) ham shu yerda amalga oshiriladi.
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import jwt
from app.core.config import BASE_DIR, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.db.database import get_db
from app.db import crud
from app.schemas import Login_user, TelegramAuth
from app.core.security import pwd_context, create_access_token, get_current_user_from_cookie

router = APIRouter()

# Tizimga kirish HTML sahifasi
@router.get("/", response_class=HTMLResponse)
def login_page():
    with open(BASE_DIR/"frontend/login.html", "r", encoding="utf-8") as f:
        return f.read()

# Web tizimga login va parol yordamida kirish
@router.post("/")
def login(user: Login_user, response: Response, db: Session = Depends(get_db)):
    row = crud.get_user_by_username(db, user.username)

    if not row:
        raise HTTPException(status_code=404, detail="foydalanuvchi mavjud emas")
    if not pwd_context.verify(user.password, str(row.password)):
        raise HTTPException(status_code=401, detail="parol to'g'ri emas")

    if user.telegram_id:
        row.telegram_id = user.telegram_id
        db.commit()

    # Muvaffaqiyatli kirish: Token yaratish
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Tokenni cookie da saqlash
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)

    return {"login": "success", "username": user.username, "token": access_token}

# Telegram Mini App orqali avtomatik tizimga kirish
@router.post("/tg_login")
def tg_login(data: TelegramAuth, response: Response, db: Session = Depends(get_db)):
    # Oldin bunday telegram account borligini bazadan tekshiramiz
    user = crud.get_user_by_telegram_id(db, data.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Ushbu Telegram ID hali ro'yxatdan o'tmagan. Iltimos, web orqali tizimga kiring.")

    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="none", secure=True)

    return {"login": "success", "username": user.username, "token": access_token}

@router.post("/link_telegram")
def link_telegram(data: TelegramAuth, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    user = crud.get_user_by_username(db, current_user)
    if user:
        user.telegram_id = data.telegram_id
        db.commit()
        return {"msg": "Telegram ID linked successfully"}
    raise HTTPException(status_code=404)

# Tizimdan chiqish va token cookie sini o'chirish, hamda telegram_id ni tozalash
@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    response.delete_cookie("access_token", httponly=True, samesite="none", secure=True)

    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = crud.get_user_by_username(db, username)
                if user:
                    user.telegram_id = None
                    db.commit()
        except Exception:
            pass # Ignore expired tokens, just clear session

    return {"msg": "logout successful"}
