# Ushbu fayl ma'lumotlar bazasi bilan ishlash uchun asosiy funksiyalarni saqlaydi (CRUD).
# Ma'lumot qo'shish, o'qish, yangilash kabi barcha jarayonlar shu yerda.
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import User, Progress, Skin, UserSkin
from app.schemas import New_user
from app.core.security import pwd_context


# Foydalanuvchini username bo'yicha qidirib topish
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

# Foydalanuvchini email bo'yicha qidirib topish
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

# Telegram ID orqali foydalanuvchini topish
def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    # use filter_by to simplify query expression
    return db.query(User).filter_by(telegram_id=telegram_id).first()

# Yangi foydalanuvchini bazaga saqlash
def create_user(user: New_user, db: Session) -> User:
    # Parolni xesh qilish
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    # Ma'lumotlarni yangilab qaytarish
    db.refresh(new_user)

    # Ensure a Progress row exists for the new user to avoid later None checks
    existing_progress = db.query(Progress).filter_by(username=new_user.username).first()
    if not existing_progress:
        prog = Progress(
            username=new_user.username,
            cookies=0.0,
            totalCookies=0.0,
            cps=0.0,
            cursor_count=0,
            grandma_count=0,
            factory_count=0
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)

    return new_user

# Telegram bot orqali kelgan yangi o'yinchini ro'yxatdan o'tkazish
def create_telegram_user(db: Session, telegram_id: int) -> User:
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
    )
    # set telegram_id separately to avoid static-analysis false positive on unexpected keyword
    new_user.telegram_id = telegram_id
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create initial progress for telegram user as well
    existing_progress = db.query(Progress).filter_by(username=new_user.username).first()
    if not existing_progress:
        prog = Progress(
            username=new_user.username,
            cookies=0.0,
            totalCookies=0.0,
            cps=0.0,
            cursor_count=0,
            grandma_count=0,
            factory_count=0
        )
        db.add(prog)
        db.commit()
        db.refresh(prog)

    return new_user

# Username orqali o'yinchi progressini topish
def get_progress_by_username(db: Session, username: str) -> Optional[Progress]:
    return db.query(Progress).filter(Progress.username == username).first()

# O'yinchi holatini (pechenye soni) saqlash yoki bazada yangilash
def update_or_create_progress(db: Session, progress_data) -> Progress:
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
def get_top_progress(db: Session, limit: int = 10) -> List[Progress]:
    return db.query(Progress).order_by(Progress.totalCookies.desc()).limit(limit).all()

# Maxsus bir o'yinchining reytingdagi o'rnini (qator raqamini) hisoblash
def get_progress_rank(db: Session, username: str) -> int:
    db_progress = get_progress_by_username(db, username)
    if not db_progress:
        return 0
    # O'zidan ko'proq pechenye yig'ganlarni sanash
    return db.query(Progress).filter(Progress.totalCookies > db_progress.totalCookies).count() + 1



def can_afford(session: Session, username: str, skin_id: int) -> bool:
    """
    Returns True if user has enough cookies to buy given skin.
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return False
    progress = session.query(Progress).filter_by(username=username).first()
    if not progress:
        return False
    skin = session.query(Skin).filter_by(id=skin_id).first()
    if not skin:
        return False
    try:
        return float(progress.cookies) >= float(skin.price)
    except (TypeError, ValueError):
        return False


def can_afford_by_user_id(session: Session, user_id: int, skin_id: int) -> bool:
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return False
    progress = session.query(Progress).filter_by(username=user.username).first()
    if not progress:
        return False
    skin = session.query(Skin).filter_by(id=skin_id).first()
    if not skin:
        return False
    try:
        return float(progress.cookies) >= float(skin.price)
    except (TypeError, ValueError):
        return False


def buy_skin(session: Session, username: str, skin_id: int) -> Dict[str, Any]:
    """
    Attempts to buy skin for a user. Returns dict with result and message.
    This function is kept simple and DB-engine compatible (avoids with_for_update which is not supported in SQLite).
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return {"ok": False, "message": "User not found", "owned": False}

    progress = session.query(Progress).filter_by(username=username).first()
    if not progress:
        return {"ok": False, "message": "User progress not found", "owned": False}

    skin = session.query(Skin).filter_by(id=skin_id).first()
    if not skin:
        return {"ok": False, "message": "Skin not found", "owned": False}

    try:
        price = float(skin.price)
    except (TypeError, ValueError):
        return {"ok": False, "message": "Invalid skin price", "owned": False}

    if price < 0:
        return {"ok": False, "message": "Invalid skin price", "owned": False}

    # check if already owned (initial quick check)
    existing = session.query(UserSkin).filter_by(user_id=user.id, skin_id=skin.id).first()
    if existing:
        return {"ok": False, "message": "Skin already owned", "owned": True}

    try:
        # Perform checks and update within a single unit of work using explicit commit/rollback.
        # Re-query current progress and ownership to reduce race window.
        p = session.query(Progress).filter_by(username=username).first()
        if p is None:
            return {"ok": False, "message": "User progress not found", "owned": False}

        # re-check ownership
        existing_tx = session.query(UserSkin).filter_by(user_id=user.id, skin_id=skin.id).first()
        if existing_tx:
            return {"ok": False, "message": "Skin already owned", "owned": True}

        if float(p.cookies) < price:
            return {"ok": False, "message": "Not enough cookies", "owned": False, "cookies": float(p.cookies)}

        # deduct price from current cookies; do not alter totalCookies
        p.cookies = float(p.cookies) - price
        if p.cookies < 0:
            p.cookies = 0.0

        # Unequip other skins for this user (use synchronize_session=False for performance)
        session.query(UserSkin).filter(UserSkin.user_id == user.id, UserSkin.equipped == True).update({"equipped": False}, synchronize_session=False)

        # Create and equip the new skin
        new_us = UserSkin(user_id=user.id, skin_id=skin.id, equipped=True)
        session.add(new_us)

        # Commit all changes
        session.commit()

        # Build skin payload to return
        skin_payload = {
            "id": skin.id,
            "name": skin.name,
            "price": float(skin.price),
            "description": skin.description,
            "rarity": skin.rarity,
            "image": skin.image,
            "type": getattr(skin, 'type', None),
            "equipped": True,
        }

        return {"ok": True, "message": "Purchase successful", "owned": True, "cookies": float(p.cookies), "skin": skin_payload}
    except Exception as e:
        # Roll back on error and return message
        try:
            session.rollback()
        except Exception:
            pass
        return {"ok": False, "message": f"Error during purchase: {e}", "owned": False}


def get_user_owned_skins(session: Session, username: str) -> List[Dict[str, Any]]:
    """
    Returns list of skins owned by the user with equipped state.
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return []
    rows = (
        session.query(Skin, UserSkin.equipped)
        .join(UserSkin, Skin.id == UserSkin.skin_id)
        .filter(UserSkin.user_id == user.id)
        .all()
    )
    result: List[Dict[str, Any]] = []
    for skin, equipped in rows:
        result.append({
            "id": skin.id,
            "name": skin.name,
            "price": float(skin.price),
            "description": skin.description,
            "rarity": skin.rarity,
            "image": skin.image,
            "equipped": bool(equipped),
        })
    return result


def get_available_skins_for_user(session: Session, username: str) -> List[Dict[str, Any]]:
    """
    Returns list of skins the user hasn't bought yet.
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return []

    owned_subq = session.query(UserSkin.skin_id).filter(UserSkin.user_id == user.id).subquery()
    skins = session.query(Skin).filter(~Skin.id.in_(owned_subq)).all()

    result: List[Dict[str, Any]] = []
    for skin in skins:
        result.append({
            "id": skin.id,
            "name": skin.name,
            "price": float(skin.price),
            "description": skin.description,
            "rarity": skin.rarity,
            "image": skin.image,
        })
    return result


def list_all_purchases(session: Session) -> List[Dict[str, Any]]:
    """
    Returns a list of all purchases: which user bought which skin and equip state.
    """
    rows = (
        session.query(User.username, Skin.id, Skin.name, UserSkin.equipped)
        .join(UserSkin, User.id == UserSkin.user_id)
        .join(Skin, Skin.id == UserSkin.skin_id)
        .all()
    )

    result: List[Dict[str, Any]] = []
    for username, skin_id, skin_name, equipped in rows:
        result.append({
            "username": username,
            "skin_id": skin_id,
            "skin_name": skin_name,
            "equipped": bool(equipped),
        })
    return result


# New helper: summary of user's skins and balance to help frontend decide
def get_user_skins_summary(session: Session, username: str) -> Dict[str, Any]:
    """
    Returns a summary:
      {
        "username": str,
        "cookies": float,
        "owned": [ {id,name,price,image,equipped} ],
        "available": [ {id,name,price,image} ],
        "affordable_ids": [int],
        "equipped_id": int | None
      }
    """
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return {"error": "user_not_found"}

    progress = session.query(Progress).filter_by(username=username).first()
    cookies = float(progress.cookies) if progress else 0.0

    owned = get_user_owned_skins(session, username)
    available = get_available_skins_for_user(session, username)

    affordable_ids = [s["id"] for s in available if float(s.get("price", 0)) <= cookies]
    equipped_id = None
    for s in owned:
        if s.get('equipped'):
            equipped_id = s.get('id')
            break

    return {
        "username": username,
        "cookies": cookies,
        "owned": owned,
        "available": available,
        "affordable_ids": affordable_ids,
        "equipped_id": equipped_id,
    }
