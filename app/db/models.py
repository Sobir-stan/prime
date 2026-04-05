# Ushbu fayl ma'lumotlar bazasining jadvallarini tuzilishini belgilaydi.
# SQLAlchemy yordamida User va Progress obyektlari yaratilgan.
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from app.db.database import Base

# Foydalanuvchilar jadvali
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
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

# Promokodlar jadvali
class Promocode(Base):
    __tablename__ = "promocodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True, nullable=False)
    reward = Column(Float, nullable=False)
    max_uses = Column(Integer, nullable=False, default=0) # 0 = cheksiz
    current_uses = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

# Qaysi o'yinchi qaysi promokodni ishlatgani haqida ma'lumot
class UsedPromocode(Base):
    __tablename__ = "used_promocodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    promocode_id = Column(Integer, ForeignKey("promocodes.id"), nullable=False)