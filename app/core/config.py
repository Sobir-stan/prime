# Ushbu fayl loyihaning asosiy sozlamalarini va o'zgaruvchilarini saqlaydi.
# Atrof-muhit (.env) faylidan ma'lumotlarni o'qiydi va boshqa joylarda ishlatish uchun tayyorlaydi.
import os
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy direktoryasini aniqlash (Dastur root gacha borish)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env faylini o'qib, muhit o'zgaruvchilariga qo'shish
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Tokenlarni shifrlash uchun maxfiy kalit va algoritm
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Tokenning amal qilish muddati (daqiqa hisobida)
ACCESS_TOKEN_EXPIRE_MINUTES = 60