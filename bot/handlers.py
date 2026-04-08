from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
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
# URL = "https://stan.uz"
URL = "https://0449-84-54-72-145.ngrok-free.app"


def check_telegram_id(message: Message):
    is_registered = False
    db = SessionLocal()
    try:
        user = crud.get_user_by_telegram_id(db, message.from_user.id)
        is_registered = bool(user)
    finally:
        db.close()
    return is_registered

# Asosiy klaviatura (menyular) ni yaratish
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏆 Reyting")
    builder.button(text="🎁 Promokod")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# O'yinni ochuvchi Inline tugma
def get_play_keyboard(message: Message):
    builder = InlineKeyboardBuilder()
    is_registered = check_telegram_id(message)
    target_url = f"{URL}/clicker?tg_id={message.from_user.id}" if is_registered else f"{URL}/?tg_id={message.from_user.id}"
    builder.button(text="🎮 Clicker O'ynash", web_app=WebAppInfo(url=target_url))
    return builder.as_markup()


# /start komandasiga javob beruvchi handler
@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # FSM (holat) ni tozalash
    await state.clear()
       
    # Asosiy menyuni chiqarish
    await message.answer("Menyular:", reply_markup=get_main_keyboard())

    # Foydalanuvchiga salomlashish va O'yin klaviaturasini ko'rsatish
    await message.answer(
        f"Salom, {message.from_user.first_name}! Clicker o'yiniga xush kelibsiz.\n\n"
        "Mini App'ni ishga tushirish uchun quyidagi 'O'ynash' tugmasini bosing:",
        reply_markup=get_play_keyboard(message)
    )

# Maxfiy modul: promokod bazada qidiriladigan umumiy yordamchi funksiya
async def _process_promo(message: Message, code: str):
    db = SessionLocal()
    try:
        user = crud.get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            await message.answer("Iltimos, oldin '🎮 Clicker O'ynash' tugmasini bosib, o'yinga kiring va hisobingizni ulang!")
            return
            
        result = crud.use_promocode(db, code, user.username)
        await message.answer(result["msg"])
    finally:
        db.close()

# Telegram orqali Promokod qabul qilish handleri (/promo KOD_NOMI)
@router.message(Command("promo"))
async def apply_promo_handler(message: Message):
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.answer("Iltimos, promokodni shunday kiriting: \n<code>/promo KOD_NOMI</code>", parse_mode="HTML")
        return
    await _process_promo(message, parts[1].strip())

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

# "🎁 Promokod" tugmasi bosilganda ishlovchi handler
@router.message(F.text == "🎁 Promokod")
async def ask_promo_handler(message: Message, state: FSMContext):
    await state.set_state(PromoState.waiting_for_promo)
    await message.answer("Iltimos, promokodni kiriting:")

# Promokod kiritish holatida ishlovchi handler (tugma orqali yuborilsa)
@router.message(PromoState.waiting_for_promo)
async def state_promo_handler(message: Message, state: FSMContext):
    await state.clear()
    await _process_promo(message, message.text.strip())
