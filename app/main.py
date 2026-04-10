from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.db.database import init_db
from app.routers import rating, login, register, clicker, promo

init_db()

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(clicker.router)
app.include_router(rating.router)
app.include_router(promo.router)
