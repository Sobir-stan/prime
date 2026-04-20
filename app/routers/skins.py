from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.schemas import PurchaseRequest

router = APIRouter(prefix="/api/skins")


@router.get('/available')
def available_skins(user_id: str = None, db: Session = Depends(get_db)):
    username = user_id
    if not username:
        raise HTTPException(status_code=400, detail='user_id required')
    skins = crud.get_available_skins_for_user(db, username)
    return skins


@router.post('/buy')
def buy_skin_api(payload: PurchaseRequest, db: Session = Depends(get_db)):
    user = payload.user_id
    skin_id = payload.skin_id
    if not user or skin_id is None:
        raise HTTPException(status_code=400, detail='user_id and skin_id required')

    res = crud.buy_skin(db, user, int(skin_id))
    # res already contains ok, message, owned, cookies, skin optionally
    if res.get('ok'):
        return res
    else:
        # Return appropriate status code for insufficient funds
        if res.get('message') == 'Not enough cookies':
            raise HTTPException(status_code=402, detail=res.get('message'))
        # already owned -> 200 with owned True for idempotency
        return res


@router.get('/owned')
def owned_skins(user_id: str = None, db: Session = Depends(get_db)):
    username = user_id
    if not username:
        raise HTTPException(status_code=400, detail='user_id required')
    return crud.get_user_owned_skins(db, username)


@router.get('/summary')
def skins_summary(user_id: str = None, db: Session = Depends(get_db)):
    username = user_id
    if not username:
        raise HTTPException(status_code=400, detail='user_id required')
    summary = crud.get_user_skins_summary(db, username)
    if summary.get('error'):
        raise HTTPException(status_code=404, detail=summary.get('error'))
    return summary
