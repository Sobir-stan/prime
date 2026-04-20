from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.db import crud
from app.schemas import CreatePromoCode, UpdatePromoCode, PromoCodeResponse
from app.core.security import get_current_user_from_cookie

router = APIRouter(prefix="/promo", tags=["promo"])

@router.post("/create_promo", response_model=PromoCodeResponse)
def create_promo(promo_data: CreatePromoCode, db: Session = Depends(get_db), current_user: str = Depends(get_current_user_from_cookie)):

    print(f"Received promo data: {promo_data}")
    try:
        existing_promo = crud.get_promo_by_code(db, promo_data.code)
        if existing_promo:
            raise HTTPException(status_code=400, detail="Bu promokod allaqachon mavjud")

        new_promo = crud.create_promo_code(db, promo_data.code, promo_data.cookies, promo_data.usage_limit, created_by_username=current_user)
        
        return PromoCodeResponse(
            id=new_promo.id,
            code=new_promo.code,
            cookies=new_promo.cookies,
            usage_limit=new_promo.usage_limit,
            active=new_promo.active,
            used_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Sana formati xato: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")

@router.get("/list", response_model=list[PromoCodeResponse])
def get_all_promos(db: Session = Depends(get_db)):

    try:
        promos = crud.get_all_promo_codes(db)
        return [PromoCodeResponse(
            id=p.id,
            code=p.code,
            cookies=p.cookies,
            usage_limit=p.usage_limit,
            active=p.active,
            used_count=p.used_count
        ) for p in promos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")

@router.put("/update_promo", response_model=PromoCodeResponse)
def update_promo(promo_data: UpdatePromoCode, db: Session = Depends(get_db)):
    try:
        existing_promo = crud.get_promo_by_code(db, promo_data.code)
        if not existing_promo:
            raise HTTPException(status_code=404, detail="Promokod topilmadi")

        updated_promo = crud.update_promo_code(db, promo_data.code, promo_data.cookies, promo_data.usage_limit)
        
        return PromoCodeResponse(
            id=updated_promo.id,
            code=updated_promo.code,
            cookies=updated_promo.cookies,
            usage_limit=updated_promo.usage_limit,
            active=updated_promo.active,
            used_count=crud.get_promo_usage_count(db, updated_promo.code)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Xato: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")

@router.put("/active_promo/{code}")
def toggle_promo(code: str, db: Session = Depends(get_db)):
    try:
        promo = crud.toggle_promo_active(db, code)
        if not promo:
            raise HTTPException(status_code=404, detail="Promokod topilmadi")
        return {"msg": f"Promokod {'faollashtirildi' if promo.active else 'faolsizlantirildi'}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")

@router.delete("/delete_promo/{code}")
def delete_promo(code: str, db: Session = Depends(get_db)):

    try:
        result = crud.delete_promo_code(db, code)
        if not result:
            raise HTTPException(status_code=404, detail="Promokod topilmadi")
        return {"msg": "Promokod muvaffaqiyatli o'chirildi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")

@router.get("/info/{code}", response_model=PromoCodeResponse)
def get_promo_info(code: str, db: Session = Depends(get_db)):
    try:
        promo = crud.get_promo_by_code(db, code)
        if not promo:
            raise HTTPException(status_code=404, detail="Promokod topilmadi")
        
        return PromoCodeResponse(
            id=promo.id,
            code=promo.code,
            cookies=promo.cookies,
            usage_limit=promo.usage_limit,
            active=promo.active,
            used_count=crud.get_promo_usage_count(db, code)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xato: {str(e)}")
