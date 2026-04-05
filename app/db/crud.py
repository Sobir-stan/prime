# Ushbu fayl ma'lumotlar bazasi bilan ishlash uchun asosiy funksiyalarni saqlaydi (CRUD).
# Ma'lumot qo'shish, o'qish, yangilash kabi barcha jarayonlar shu yerda.
from sqlalchemy.orm import Session
from app.db.models import User, Progress, Promocode, UsedPromocode
from app.schemas import New_user, PromocodeCreate
from app.core.security import pwd_context

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

# Yangi promokod yaratish
def create_promocode(db: Session, promo: PromocodeCreate):
    db_promo = Promocode(
        code=promo.code,
        reward=promo.reward,
        max_uses=promo.max_uses,
        is_active=promo.is_active
    )
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    return db_promo

# Barcha promokodlarni admin uchun qaytarish
def get_all_promocodes(db: Session):
    return db.query(Promocode).all()

# Promokod faolligini o'zgartirish (yoqish/o'chirish)
def toggle_promocode(db: Session, promo_id: int, is_active: bool):
    promo = db.query(Promocode).filter(Promocode.id == promo_id).first()
    if promo:
        promo.is_active = is_active
        db.commit()
        db.refresh(promo)
    return promo

# O'yinchi tomonidan promokodni ishlatish mantig'i
def use_promocode(db: Session, code: str, username: str):
    promo = db.query(Promocode).filter(Promocode.code == code).first()
    
    if not promo:
        return {"success": False, "msg": "Bunday promokod mavjud emas!"}
    if not promo.is_active:
        return {"success": False, "msg": "Ushbu promokod nofaol (o'chirilgan)."}
    if promo.max_uses > 0 and promo.current_uses >= promo.max_uses:
        return {"success": False, "msg": "Kechirasiz, ushbu promokodning ishlatilish limiti tugagan."}
    
    # Oldin ishlatganligini tekshirish
    used = db.query(UsedPromocode).filter(UsedPromocode.username == username, UsedPromocode.promocode_id == promo.id).first()
    if used:
        return {"success": False, "msg": "Siz bu promokodni allaqachon ishlatgansiz!"}
        
    # Mukofotni o'yinchi hisobiga yozish
    prog = get_progress_by_username(db, username)
    if not prog:
        prog = Progress(username=username, cookies=promo.reward, totalCookies=promo.reward, cps=0, cursor_count=0, grandma_count=0, factory_count=0)
        db.add(prog)
    else:
        prog.cookies += promo.reward
        prog.totalCookies += promo.reward
    
    # Promokodning umumiy ishlash sonini oshirish
    promo.current_uses += 1
    # Bu odam xuddi shu kodni qayta ishlata olmasligi uchun belgilash
    new_used = UsedPromocode(username=username, promocode_id=promo.id)
    db.add(new_used)
    
    db.commit()
    return {"success": True, "msg": f"Tabriklaymiz! Sizga {int(promo.reward)} ta pechenye bonus sifatida qo'shildi!"}