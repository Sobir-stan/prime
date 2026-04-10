from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from app.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    telegram_id = Column(Integer, unique=True, index=True, nullable=True)
    is_admin = Column(Boolean, default=False)

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"), unique=True, index=True, nullable=False)
    cookies = Column(Float, nullable=False, default=0)
    totalCookies = Column(Float, nullable=False, default=0)
    cps = Column(Float, nullable=False, default=0)
    cursor_count = Column(Integer, nullable=False, default=0)
    grandma_count = Column(Integer, nullable=False, default=0)
    factory_count = Column(Integer, nullable=False, default=0)

class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True, nullable=False)
    cookies = Column(Float, nullable=False)
    usage_limit = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

class UsedPromo(Base):
    __tablename__ = "used_promos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, nullable=False)
    username = Column(String, ForeignKey("users.username"), nullable=False)
