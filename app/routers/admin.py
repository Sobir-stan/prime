from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.core.config import BASE_DIR
from app.core.security import get_current_user_from_cookie
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


