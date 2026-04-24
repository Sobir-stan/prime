from sqlalchemy.orm import Session
from app.db.models import User, Progress, PromoCode, UsedPromo
from app.schemas import New_user, SaveProgress
from app.core.security import pwd_context
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(user: New_user, db: Session):
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_telegram_user(db: Session, telegram_id: int):
    base_username = f"user_{telegram_id}"
    username = base_username
    counter = 1
    while get_user_by_username(db, username):
        username = f"{base_username}_{counter}"
        counter += 1
        
    hashed = pwd_context.hash(f"tg_pwd_{telegram_id}")
    new_user = User(
        username=username,
        email=f"{username}@telegram.com",
        password=hashed,
        telegram_id=telegram_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_progress_by_username(db: Session, username: str):
    return db.query(Progress).filter(Progress.username == username).first()

def update_or_create_progress(db: Session, progress_data: SaveProgress):
    db_progress = get_progress_by_username(db, progress_data.username)
    
    if not db_progress:
        new_progress = Progress(
            username=progress_data.username,
            cookies=progress_data.cookie_delta,
            totalCookies=progress_data.cookie_delta,
            cps=progress_data.cps,
            cursor_count=progress_data.cursor_count,
            grandma_count=progress_data.grandma_count,
            factory_count=progress_data.factory_count
        )
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        return new_progress
    else:
        db_progress.cookies += progress_data.cookie_delta
        
        # Defensive check: totalCookies should only ever increase from client-side activity
        if progress_data.cookie_delta > 0:
            db_progress.totalCookies += progress_data.cookie_delta
        
        db_progress.cps = progress_data.cps
        db_progress.cursor_count = progress_data.cursor_count
        db_progress.grandma_count = progress_data.grandma_count
        db_progress.factory_count = progress_data.factory_count
        
        db.commit()
        db.refresh(db_progress)
        return db_progress

def get_top_progress(db: Session, limit: int = 10):
    return db.query(Progress).order_by(Progress.totalCookies.desc()).limit(limit).all()

def get_progress_rank(db: Session, username: str):
    db_progress = get_progress_by_username(db, username)
    if not db_progress:
        return 0
    return db.query(Progress).filter(Progress.totalCookies > db_progress.totalCookies).count() + 1

def get_promo_by_code(db: Session, code: str):
    return db.query(PromoCode).filter(PromoCode.code.ilike(code)).first()

def is_promo_used_by_user(db: Session, code: str, username: str):
    return db.query(UsedPromo).filter(UsedPromo.code.ilike(code), UsedPromo.username == username).first() is not None

def use_promo(db: Session, code: str, username: str):
    used = UsedPromo(code=code, username=username)
    db.add(used)

def add_bonus_cookies(db: Session, username: str, bonus: float):
    progress = get_progress_by_username(db, username)
    if not progress:
        progress = Progress(username=username, cookies=bonus, totalCookies=bonus, cps=0.0, cursor_count=0, grandma_count=0, factory_count=0)
        db.add(progress)
    else:
        progress.cookies += bonus
        progress.totalCookies += bonus
    db.flush()
    db.refresh(progress)
    return progress

def get_promo_usage_count(db: Session, code: str):
    return db.query(UsedPromo).filter(UsedPromo.code.ilike(code)).count()

def apply_promo_code_to_user(db: Session, code: str, username: str):
    promo = get_promo_by_code(db, code)
    if not promo:
        raise ValueError("Bunday Promokod mavjud emas")

    if not promo.active:
        raise ValueError("Bu promokod faolsizlantirilgan")

    used_count = get_promo_usage_count(db, code)
    if used_count >= promo.usage_limit:
        raise ValueError("Bu promokod ishlatish limiti tugagan")

    if is_promo_used_by_user(db, code, username):
        raise ValueError("Bu promokod allaqachon ishlatilgan")

    add_bonus_cookies(db, username, promo.cookies)
    use_promo(db, code, username)
    
    return promo

def create_promo_code(db: Session, code: str, cookies: float, usage_limit: int, created_by_username=None):
    promo = PromoCode(code=code, cookies=cookies, usage_limit=usage_limit, active=True, created_by_username=created_by_username)
    db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo

def get_all_promo_codes(db: Session):
    promos = db.query(PromoCode).all()
    for promo in promos:
        promo.used_count = get_promo_usage_count(db, promo.code)
    return promos

def update_promo_code(db: Session, code: str, new_cookies: float, new_usage_limit: int):
    promo = get_promo_by_code(db, code)
    if promo:
        promo.cookies = new_cookies
        promo.usage_limit = new_usage_limit
        db.commit()
        db.refresh(promo)
        return promo
    return None

def toggle_promo_active(db: Session, code: str):
    promo = get_promo_by_code(db, code)
    if promo:
        promo.active = not promo.active
        db.commit()
        db.refresh(promo)
        return promo
    return None

def delete_promo_code(db: Session, code: str):
    promo = get_promo_by_code(db, code)
    if promo:
        db.delete(promo)
        db.commit()
        return True
    return False
