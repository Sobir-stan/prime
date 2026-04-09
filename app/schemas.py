from pydantic import BaseModel, Field

# Ushbu fayl Pydantic modellarini saqlaydi (sxemalar).
# Bu modellar mijozdan (client) kelayotgan JSON ma'lumotlarni tekshirish va tozalash uchun ishlatiladi.

# Yangi foydalanuvchi ro'yxatdan o'tayotganida keladigan ma'lumotlar
class New_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=3)

from typing import Optional

# Tizimga kirish (Login) vaqtida keladigan shakl
class Login_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)
    telegram_id: Optional[int] = None

# O'yin progressini saqlash so'rovining formati
class SaveProgress(BaseModel):
    username: str
    cookies: float
    totalCookies: float
    cps: float
    cursor_count : int
    grandma_count : int
    factory_count : int

class TelegramAuth(BaseModel):
    telegram_id: int

