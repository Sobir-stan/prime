from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.config import BASE_DIR
from app.db.database import get_db
from app.db import crud
from app.schemas import SaveProgress
from app.core.security import get_current_user_from_cookie
from pydantic import BaseModel
from datetime import datetime

class ApplyPromo(BaseModel):
    code: str

router = APIRouter()

@router.get("/clicker", response_class=HTMLResponse)
def clicker_page():
    with open(BASE_DIR/"frontend/clicker.html", "r", encoding="utf-8") as f:
        return f.read()

@router.post("/save_progress")
def save_progress(progress: SaveProgress, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != progress.username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    crud.update_or_create_progress(db, progress)
    return {"msg": "progress saqlandi"}

@router.get("/load_progress/{username}")
def load_progress(username: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    row = crud.get_progress_by_username(db, username)
    if not row:
        return {
            "username": username,
            "cookies" : 0.0,
            "totalCookies" : 0.0,
            "cps" : 0.0,
            "cursor_count" : 0,
            "grandma_count" : 0,
            "factory_count" : 0,
        }
    return {
        "username": row.username,
        "cookies" : row.cookies,
        "totalCookies" : row.totalCookies,
        "cps" : row.cps,
        "cursor_count" : row.cursor_count,
        "grandma_count" : row.grandma_count,
        "factory_count" : row.factory_count,
    }

@router.post("/apply_promo")
def apply_promo(promo: ApplyPromo, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    code = promo.code.upper().strip()
    promo_db = crud.get_promo_by_code(db, code)
    if not promo_db:
        return {"success": False, "message": "Bunday Promokod mavjud emas"}

    if datetime.utcnow() > promo_db.expires_at:
        return {"success": False, "message": "Promokod muddati utgan"}

    if crud.is_promo_used_by_user(db, code, current_user):
        return {"success": False, "message": "Bu promokod allaqachon ishlatilgan"}


    crud.add_bonus_cookies(db, current_user, 10000)
    crud.use_promo(db, code, current_user)
    return {"success": True, "message": "10,000 pisheniya bonus sifatida qo'shildi!"}
