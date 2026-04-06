from sqlalchemy.orm import Session
from app.db.models import User, Progress, PromoCode, UsedPromo
from app.schemas import New_user
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

def update_or_create_progress(db: Session, progress_data):
    db_progress = get_progress_by_username(db, progress_data.username)
    if not db_progress:
        new_progress = Progress(
            username=progress_data.username,
            cookies=progress_data.cookies,
            totalCookies=progress_data.totalCookies,
            cps=progress_data.cps,
            cursor_count=progress_data.cursor_count,
            grandma_count=progress_data.grandma_count,
            factory_count=progress_data.factory_count
        )
        db.add(new_progress)
        db_progress = new_progress
    else:
        db_progress.cookies = progress_data.cookies
        db_progress.totalCookies = progress_data.totalCookies
        db_progress.cps = progress_data.cps
        db_progress.cursor_count = progress_data.cursor_count
        db_progress.grandma_count = progress_data.grandma_count
        db_progress.factory_count = progress_data.factory_count
    db.commit()
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
    db.commit()

def add_bonus_cookies(db: Session, username: str, bonus: float):
    progress = get_progress_by_username(db, username)
    if progress:
        progress.cookies += bonus
        progress.totalCookies += bonus
        db.commit()
        return progress
    return None
