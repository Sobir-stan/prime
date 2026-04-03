# Ushbu fayl ma'lumotlar bazasining jadvallarini tuzilishini belgilaydi.
# SQLAlchemy yordamida User va Progress obyektlari yaratilgan.
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.database import Base

# Foydalanuvchilar jadvali
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

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