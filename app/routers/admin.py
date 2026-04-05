from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.core.config import BASE_DIR
from app.core.security import get_current_user_from_cookie
from app.schemas import PromocodeCreate, PromocodeToggle
from app.db import crud
from app.db.database import get_db
from sqlalchemy.orm import Session

# Ushbu fayl faqat admin uchun mo'ljallangan maxsus funksiyalar
# va Admin panel sahifasini o'z ichiga oladi.

router = APIRouter()

# Admin boshqaruv oynasi
@router.get("/admin", response_class=HTMLResponse)
def admin_page(current_user: str = Depends(get_current_user_from_cookie)):
    # Faqat 'admin' loginli foydalanuvchini kiritish
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Kechirasiz, siz admin emassiz!")
        
    with open(BASE_DIR / "frontend/admin.html", "r", encoding="utf-8") as f:
        return f.read()

# Barcha promokodlarni qaytarish API (Admin uchun)
@router.get("/admin/promocodes")
def get_promocodes(db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")
    return crud.get_all_promocodes(db)

# Yangi promokod yaratish API
@router.post("/admin/promocodes")
def create_promo(promo: PromocodeCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")
    try:
        new_promo = crud.create_promocode(db, promo)
        return {"success": True, "msg": "Promokod muvaffaqiyatli yaratildi!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ushbu kod avval yaratilgan bo'lishi mumkin.")

# Promokodni yoqish/o'chirish API
@router.put("/admin/promocodes/{promo_id}/toggle")
def toggle_promo(promo_id: int, toggle: PromocodeToggle, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):
    if current_user != "admin":
        raise HTTPException(status_code=403, detail="Ruxsat etilmagan")
    updated = crud.toggle_promocode(db, promo_id, toggle.is_active)
    if not updated:
        raise HTTPException(status_code=404, detail="Promokod topilmadi")
    return {"success": True, "msg": "Holat o'zgartirildi"}
