# Ushbu fayl xavfsizlik va avtorizatsiya jarayonlariga javob beradi.
# Parollarni shifrlash va JWT tokenlarni yaratish hamda tekshirish shu yerda amalga oshiriladi.
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from passlib.context import CryptContext

from app.core.config import SECRET_KEY, ALGORITHM

# Parollarni xesh qilish (shifrlash) uchun obyekt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Yangi kirish tokenini (JWT) yaratuvchi funksiya
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    
    # Token tugash vaqtini hisoblash
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    # Ma'lumotlarni shifrlangan tokenga aylantirish
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Cookies yoki Headers orqali foydalanuvchini aniqlash funksiyasi
def get_current_user_from_cookie(request: Request):
    # Oldin cookie fileni tekshirish
    token = request.cookies.get("access_token")
    if not token:
        # Authorization header orqali avtorizatsiyani tekshirish (fallback)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    # Agar token umuman topilmasa xato qaytarish
    if not token:
        raise HTTPException(status_code=401, detail="Token topilmadi. (Token not found)")
        
    try:
        # Tokenni ochib ko'rish va ichidan username ni olish
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Yaroqsiz token. (Invalid)")
        return username
    except jwt.ExpiredSignatureError:
        # Token vaqti tugagan bo'lsa xato qaytarish
        raise HTTPException(status_code=401, detail="Token muddati tugagan. (Expired)")
    except jwt.PyJWTError:
        # Token tuzilishi noto'g'ri bo'lsa
        raise HTTPException(status_code=401, detail="Xato token. (Invalid token)")
