# Ushbu fayl ma'lumotlar bazasining jadvallarini tuzilishini belgilaydi.
# SQLAlchemy yordamida User va Progress obyektlari yaratilgan.
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, Boolean
from app.db.database import Base

# Foydalanuvchilar jadvali
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    # Telegram ID (optional) — qo'shildi, agar bot orqali ro'yxatdan o'tsa saqlanadi
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)

# O'yinchining to'plagan ballari va xaridlari jadvali
class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # Ushbu jadvalni users jadvaliga bog'lash (Tashqi kalit)
    username = Column(String, ForeignKey("users.username"), unique=True, index=True, nullable=False)
    cookies = Column(Float, nullable=False, default=0)
    totalCookies = Column(Float, nullable=False, default=0)
    cps = Column(Float, nullable=False, default=0)
    cursor_count = Column(Integer, nullable=False, default=0)
    grandma_count = Column(Integer, nullable=False, default=0)
    factory_count = Column(Integer, nullable=False, default=0)


class Skin(Base):
    __tablename__ = "skins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False, default=0)
    description = Column(String, nullable=True)
    rarity = Column(String, nullable=True)
    image = Column(String, nullable=True)
    # deterministic skin type used by frontend to select visuals (e.g. 'cookie', 'egg', 'orange', 'coin')
    type = Column(String, nullable=True)

class UserSkin(Base):
    __tablename__ = "user_skins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    skin_id = Column(Integer, ForeignKey("skins.id"), nullable=False, index=True)
    equipped = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("user_id", "skin_id", name="uix_user_skin"),)