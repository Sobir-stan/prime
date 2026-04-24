from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.config import BASE_DIR
from app.db.database import get_db
from app.db import crud
from app.schemas import SaveProgress
from app.core.security import get_current_user_from_cookie, get_current_admin
from pydantic import BaseModel

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
        return {"username": username, "cookies": 0.0, "totalCookies": 0.0, "cps": 0.0, "cursor_count": 0, "grandma_count": 0, "factory_count": 0}
    return {"username": row.username, "cookies": row.cookies, "totalCookies": row.totalCookies, "cps": row.cps, "cursor_count": row.cursor_count, "grandma_count": row.grandma_count, "factory_count": row.factory_count}

@router.post("/apply_promo")
def apply_promo(promo: ApplyPromo, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    code = promo.code.upper().strip()
    try:
        with db.begin():
            promo_obj = crud.apply_promo_code_to_user(db, code, current_user)
            return {"success": True, "message": f"{promo_obj.cookies} pecheniye bonus sifatida qo'shildi!"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Xatolik yuz berdi")

@router.get("/admin", response_class=HTMLResponse)
def admin_page(current_admin: str = Depends(get_current_admin)):
    with open(BASE_DIR/"frontend/admin.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/get_rank") 
def get_rank(db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)): 
    rank = crud.get_progress_rank(db, current_user) 
    return {"rank": rank}

@router.post("/link_tg")
def link_tg(tg_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    user = crud.get_user_by_username(db, current_user)
    if user and user.telegram_id is not None:
        user.telegram_id = None
        db.commit()
    existing_user_with_tg_id = crud.get_user_by_telegram_id(db, tg_id)
    if existing_user_with_tg_id:
        existing_user_with_tg_id.telegram_id = None
        db.commit()
    if user:
        user.telegram_id = tg_id
        db.commit()
    return {"msg": "linked"}
