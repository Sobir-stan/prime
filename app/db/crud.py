# Ushbu fayl ma'lumotlar bazasi bilan ishlash uchun asosiy funksiyalarni saqlaydi (CRUD).
# Ma'lumot qo'shish, o'qish, yangilash kabi barcha jarayonlar shu yerda.
from sqlalchemy.orm import Session
from app.db.models import User, Progress, News
from app.schemas import New_user
from app.core.security import pwd_context
from datetime import datetime, timezone

# Foydalanuvchini username bo'yicha qidirib topish
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Foydalanuvchini email bo'yicha qidirib topish
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Telegram ID orqali foydalanuvchini topish
def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

# Yangi foydalanuvchini bazaga saqlash
def create_user(user: New_user, db: Session):
    # Parolni xesh qilish
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    # Ma'lumotlarni yangilab qaytarish
    db.refresh(new_user)
    return new_user

# Telegram bot orqali kelgan yangi o'yinchini ro'yxatdan o'tkazish
def create_telegram_user(db: Session, telegram_id: int):
    base_username = f"user_{telegram_id}"
    username = base_username
    counter = 1
    
    # Agar bunday username bor bo'lsa, raqam qo'shib tekshirish
    while get_user_by_username(db, username):
        username = f"{base_username}_{counter}"
        counter += 1
        
    # Telegram foydalanuvchisi uchun avtomatik parol
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

# Username orqali o'yinchi progressini topish
def get_progress_by_username(db: Session, username: str):
    return db.query(Progress).filter(Progress.username == username).first()

# O'yinchi holatini (pechenye soni) saqlash yoki bazada yangilash
def update_or_create_progress(db: Session, progress_data):
    db_progress = get_progress_by_username(db, progress_data.username)
    
    # Agar progress hali yo'q bo'lsa yangi obyekt yaratish
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
        # Bor bo'lsa uni yangilash
        db_progress.cookies = progress_data.cookies
        db_progress.totalCookies = progress_data.totalCookies
        db_progress.cps = progress_data.cps
        db_progress.cursor_count = progress_data.cursor_count
        db_progress.grandma_count = progress_data.grandma_count
        db_progress.factory_count = progress_data.factory_count
        
    db.commit()
    return db_progress

# Reyting uchun eng ko'p pechenyeyga ega bo'lgan top o'yinchilarni olish
def get_top_progress(db: Session, limit: int = 10):
    return db.query(Progress).order_by(Progress.totalCookies.desc()).limit(limit).all()

# Maxsus bir o'yinchining reytingdagi o'rnini (qator raqamini) hisoblash
def get_progress_rank(db: Session, username: str):
    db_progress = get_progress_by_username(db, username)
    if not db_progress:
        return 0
    # O'zidan ko'proq pechenye yig'ganlarni sanash
    return db.query(Progress).filter(Progress.totalCookies > db_progress.totalCookies).count() + 1


# --- News CRUD ---
def list_news(db: Session):
    """Return all news ordered newest first."""
    return db.query(News).order_by(News.created_at.desc()).all()


def create_news(db: Session, text: str, active: bool = True):
    n = News(text=text, active=active, created_at=datetime.now(timezone.utc))
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def set_news_active(db: Session, news_id: int, active: bool):
    n = db.query(News).filter(News.id == news_id).first()
    if not n:
        return False
    n.active = active
    db.commit()
    return True


def delete_news(db: Session, news_id: int):
    n = db.query(News).filter(News.id == news_id).first()
    if not n:
        return False
    db.delete(n)
    db.commit()
    return True


def delete_all_news(db: Session):
    db.query(News).delete()
    db.commit()
    return True


