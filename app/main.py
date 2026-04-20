# Ushbu fayl FastAPI dasturining asosiy ishga tushirish nuqtasi hisoblanadi.
# U barcha marshrutlarni (router) ulaydi, bazani ishga tushiradi va statik fayllarni xizmat qiladi.
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.db.database import init_db
from app.routers import rating, login, register, clicker, skins

# Ma'lumotlar bazasini ishga tushirish
init_db()

# FastAPI dasturini yaratish
app = FastAPI()

# Frontend papkasidagi statik fayllarni (HTML, CSS, JS) ulash
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve requests under /.well-known (e.g. Chrome DevTools app-specific probe)
app.mount("/.well-known", StaticFiles(directory="frontend/.well-known"), name="well_known")

# Turli xil marshrutlarni loyihaga kiritish
app.include_router(login.router)
app.include_router(register.router)
app.include_router(clicker.router)
app.include_router(rating.router)
app.include_router(skins.router)
