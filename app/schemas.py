from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, JSON

from app.db.database import Base


# Ushbu fayl Pydantic modellarini saqlaydi (sxemalar).
# Bu modellar mijozdan (client) kelayotgan JSON ma'lumotlarni tekshirish va tozalash uchun ishlatiladi.

# Test uchun namunaviy model
class Body_test(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    age: int = Field(gt=0, le=100)

# Yangi foydalanuvchi ro'yxatdan o'tayotganida keladigan ma'lumotlar
class New_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=3)

# Tizimga kirish (Login) vaqtida keladigan shakl
class Login_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)

# O'yin progressini saqlash so'rovining formati
class SaveProgress(BaseModel):
    username: str
    cookies: float
    totalCookies: float
    cps: float
    cursor_count : int
    grandma_count : int
    factory_count : int

# Telegram orqali avtomatik tizimga kirish auth ma'lumotlari
class TelegramAuth(BaseModel):
    telegram_id: int
    username: str

class Progress(Base):
    __tablename__ = "progress"

    user_id = Column(Integer, primary_key=True)
    cookies = Column(Integer, default=0)

    active_skin = Column(String, default="cookie.png")
    unlocked_skins = Column(JSON, default=["cookie.png"])