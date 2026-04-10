from pydantic import BaseModel, Field


class Body_test(BaseModel):
    username: str = Field(min_length=5, max_length=20)
    age: int = Field(gt=0, le=100)

class New_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=3)


class Login_user(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3)


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
    username: str

class CreatePromoCode(BaseModel):
    code: str
    cookies: float
    usage_limit: int

class UpdatePromoCode(BaseModel):
    code: str
    cookies: float
    usage_limit: int

class PromoCodeResponse(BaseModel):
    id: int
    code: str
    cookies: float
    usage_limit: int
    active: bool
    used_count: int
    
    class Config:
        from_attributes = True
