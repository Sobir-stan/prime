from pydantic import BaseModel, Field
from typing import List, Optional

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

# Skin DTOs for API
class SkinOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    rarity: Optional[str] = None
    image: Optional[str] = None
    type: Optional[str] = None

class UserOwnedSkin(SkinOut):
    equipped: bool = False

class PurchaseResult(BaseModel):
    ok: bool
    message: str
    owned: bool = False

# New: request/response schemas for purchase API
class PurchaseRequest(BaseModel):
    user_id: str
    skin_id: int

class PurchaseResponse(PurchaseResult):
    cookies: Optional[float] = None
    skin: Optional[SkinOut] = None

