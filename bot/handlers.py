from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.db.database import SessionLocal
from app.db.models import Progress
from app.db import crud

# Ushbu fayl aiogram orqali Telegram botning xabarlarini qayta ishlashni (handler) taminlaydi.
# Komandalar (/start), menyu tugmalari va WebApp havolasi shu faylda yaratiladi va sozlanadi.

router = Router()

class PromoState(StatesGroup):
    waiting_for_promo = State()

# WebApp ga yo'naltiruvchi havola (Ngrok yoki sizning domeningiz)
URL = "https://d8d4-213-230-86-180.ngrok-free.app"

# Asosiy klaviatura (menyular) ni yaratish
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()

    # WebApp tugmasini qo'shish
    builder.button(text="🎮 Clicker O'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))
    builder.button(text="🏆 Reyting")
    builder.button(text="💼 Vazifalar")
    builder.button(text="🎁 Promokod")
    # Tugmalarni ustun qilib joylash
    builder.adjust(1, 2, 1)
    return builder.as_markup(resize_keyboard=True)

# /start komandasiga javob beruvchi handler
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # FSM (holat) ni tozalash
    await state.clear()
    
    # Foydalanuvchiga salomlashish va klaviaturani ko'rsatish
    await message.answer(
        f"Salom, {message.from_user.first_name}! Clicker o'yiniga xush kelibsiz.\n\n"
        "Mini App'ni ishga tushirish uchun 'Clicker O'ynash' tugmasini bosing.",
        reply_markup=get_main_keyboard()
    )

# Telegram orqali Promokod qabul qilish handleri
@router.message(Command("promo"))
async def apply_promo_handler(message: Message):
    # Foydalanuvchi xabari quyidagicha keladi: "/promo SUPER100"
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("Iltimos, promokodni shunday kiriting: \n<code>/promo KOD_NOMI</code>", parse_mode="HTML")
        return
    
    code = parts[1].strip()
    
    db = SessionLocal()
    try:
        # Baza bo'yicha userni topish (yoki yaratish)
        user = crud.get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            user = crud.create_telegram_user(db, message.from_user.id)
            
        # Promokod funksiyasiga berish
        result = crud.use_promocode(db, code, user.username)
        await message.answer(result["msg"])
    finally:
        db.close()

# "🏆 Reyting" tugmasi bosilganda ishlovchi handler
@router.message(F.text == "🏆 Reyting")
async def rating_handler(message: Message, state: FSMContext):
    await state.clear()
    db = SessionLocal()
    try:
        # Eng ko'p pechenye yig'gan Top-10 ni bazadan olish
        top = db.query(Progress).order_by(Progress.totalCookies.desc()).limit(10).all()
        # Agar reyting bo'sh bo'lsa
        if not top:
            await message.answer("Reyting hozircha bo'sh.")
            return

        response = "🏆 <b>TOP 10 O'yinchilar</b> 🏆\n\n"
        # Reyting ro'yxatini matn sifatida yasash
        for i, p in enumerate(top, 1):
            response += f"{i}. {p.username} — {int(p.totalCookies)} ta pechenye\n"
        
        # HTML formatida xabarni yuborish
        await message.answer(response, parse_mode="HTML")
    finally:
        # Bazani ulanishni majburiy yopish
        db.close()

# "💼 Vazifalar" tugmasi bosilganda ishlovchi handler
@router.message(F.text == "💼 Vazifalar")
async def tasks_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bu yerda vazifalar bo'ladi (masalan, kanallarga obuna bo'lish). Bu funksiya hali ishlab chiqilmoqda!")

# "🎁 Promokod" tugmasi bosilganda ishlovchi handler
@router.message(F.text == "🎁 Promokod")
async def ask_promo_handler(message: Message, state: FSMContext):
    await state.set_state(PromoState.waiting_for_promo)
    await message.answer("Iltimos, promokodni kiriting:")

# Promokod kiritish holatida ishlovchi handler
@router.message(PromoState.waiting_for_promo)
async def state_promo_handler(message: Message, state: FSMContext):
    await state.clear()
    code = message.text.strip()
    
    db = SessionLocal()
    try:
        user = crud.get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            user = crud.create_telegram_user(db, message.from_user.id)
            
        result = crud.use_promocode(db, code, user.username)
        await message.answer(result["msg"])
    finally:
        db.close()
