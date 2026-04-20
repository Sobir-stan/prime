# Ushbu fayl Clicker o'yini jarayoniga javob beradigan marshrutlarni saqlaydi.
# O'yin holatini saqlash (save) va yuklash (load) shu yerda joylashgan.
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.config import BASE_DIR
from app.db.database import get_db
from app.db import crud
from app.schemas import SaveProgress
from app.core.security import get_current_user_from_cookie

router = APIRouter()

# Clicker sahifasini brauzerga yuborish
@router.get("/clicker", response_class=HTMLResponse)
def clicker_page():
    with open(BASE_DIR/"frontend/clicker.html", "r", encoding="utf-8") as f:
        return f.read()

# O'yinchi holatini saqlab qo'yish
@router.post("/save_progress")
def save_progress(progress: SaveProgress, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    # Agar token egasi o'zi bo'lmasa, xato qaytarish
    if current_user != progress.username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    crud.update_or_create_progress(db, progress)
    return {"msg": "progress saqlandi"}

# O'yin boshlanganda o'yinchi ma'lumotlarini bazadan yuklab olish
@router.get("/load_progress/{username}")
def load_progress(username: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    # Ruxsatni tekshirish
    if current_user != username:
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")

    row = crud.get_progress_by_username(db, username)
    # Agar yangi bo'lsa barcha ko'rsatkichlar 0 qaytadi
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


# Provide active news messages for the clicker frontend (JSON)
@router.get("/news")
def get_news(db: Session = Depends(get_db)):
    items = crud.list_news(db)
    # return only active messages
    active = [
        {"id": n.id, "text": n.text, "created_at": n.created_at.isoformat()} for n in items if getattr(n, "active", True)
    ]
    return {"news": active}


# Admin / API endpoints for managing news (used by admin.html or other tools)
@router.post("/news")
def create_news(payload: dict, db: Session = Depends(get_db)):
    text = payload.get('text') if isinstance(payload, dict) else None
    if not text:
        return {"error": "text required"}
    n = crud.create_news(db, text)
    return {"id": n.id, "text": n.text, "created_at": n.created_at.isoformat(), "active": n.active}


@router.post("/news/{news_id}/activate")
def activate_news(news_id: int, db: Session = Depends(get_db)):
    ok = crud.set_news_active(db, news_id, True)
    return {"ok": ok}


@router.post("/news/{news_id}/deactivate")
def deactivate_news(news_id: int, db: Session = Depends(get_db)):
    ok = crud.set_news_active(db, news_id, False)
    return {"ok": ok}


@router.delete("/news/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_news(db, news_id)
    return {"ok": ok}


@router.delete("/news")
def delete_all_news(db: Session = Depends(get_db)):
    crud.delete_all_news(db)
    return {"ok": True}


