from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.db.database import SessionLocal
from app.db.models import Progress, PromoCode, UsedPromo
from app.db import crud
from datetime import datetime

# Ushbu fayl aiogram orqali Telegram botning xabarlarini qayta ishlashni (handler) taminlaydi.
# Komandalar (/start), menyu tugmalari va WebApp havolasi shu faylda yaratiladi va sozlanadi.

router = Router()

# WebApp ga yo'naltiruvchi havola (Ngrok yoki sizning domeningiz)
URL = "http://localhost:8000"

# Promokod kiritsah uchun holat (State)
class PromoStates(StatesGroup):
    waiting_for_promo = State()


# Asosiy klaviatura (menyular) ni yaratish
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()

    # WebApp tugmasini qo'shish
    builder.button(text="🎮 Clicker O'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))
    builder.button(text="🏆 Reyting")
    builder.button(text="💼 Vazifalar")
    builder.button(text="🎁 PROMOKOD")
    # Tugmalarni ustun qilib joylash
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        f"Salom, {message.from_user.first_name}! Clicker o'yiniga xush kelibsiz.\n\n"
        "Mini App'ni ishga tushirish uchun 'Clicker O'ynash' tugmasini bosing.",
        reply_markup=get_main_keyboard()
    )


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

        response = "🏆 **TOP 10 O'yinchilar** 🏆\n\n"
        # Reyting ro'yxatini matn sifatida yasash
        for i, p in enumerate(top, 1):
            response += f"{i}. {p.username} — {int(p.totalCookies)} ta pechenye\n"

        # Markdown formatida xabarni yuborish
        await message.answer(response, parse_mode="Markdown")
    finally:
        # Bazani ulanishni majburiy yopish
        db.close()


# "💼 Vazifalar" tugmasi bosilganda ishlovchi handler
@router.message(F.text == "💼 Vazifalar")
async def tasks_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Bu yerda vazifalar bo'ladi (masalan, kanallarga obuna bo'lish). Bu funksiya hali ishlab chiqilmoqda!")


@router.message(F.text == "🎁 PROMOKOD")
async def promo_code_button(message: Message, state: FSMContext):
    await state.set_state(PromoStates.waiting_for_promo)
    await message.answer("Iltimos Promokodni kiriting:")


@router.message(PromoStates.waiting_for_promo)
async def process_promo_code(message: Message, state: FSMContext):
    code = message.text.upper().strip()
    username = message.from_user.username or f"user_{message.from_user.id}"
    
    db = SessionLocal()
    try:
        # Promokodni bazadan qidirish
        promo = crud.get_promo_by_code(db, code)
        
        # Promokod mavjudligini tekshirish
        if not promo:
            await message.answer("❌ Bunday promokod mavjud emas!")
            await state.clear()
            return
        
        # Promokod faol ekanligini tekshirish
        if not promo.active:
            await message.answer("❌ Bu promokod faolsizlantirilgan!")
            await state.clear()
            return
        
        # Promokod muddati tugganligini tekshirish
        if datetime.utcnow() > promo.expires_at:
            await message.answer("❌ Promokod muddati tugagan!")
            await state.clear()
            return
        
        # Promokod ishlatish limitini tekshirish
        used_count = crud.get_promo_usage_count(db, code)
        if used_count >= promo.usage_limit:
            await message.answer("❌ Bu promokod ishlatish limiti tugagan!")
            await state.clear()
            return
        
        # Foydalanuvchi bu promokodni allaqachon ishlatganligini tekshirish
        if crud.is_promo_used_by_user(db, code, username):
            await message.answer("❌ Siz bu promokodni allaqachon ishlatgansiz!")
            await state.clear()
            return
        
        # Promokod bajarilishi: bonus pechenye qo'shish
        crud.add_bonus_cookies(db, username, promo.cookies)
        crud.use_promo(db, code, username)
        
        await message.answer(
            f"✅ Tabriklaymiz! 🍪 {int(promo.cookies)} ta pechenye bonus sifatida qo'shildi!\n\n"
            f"Promokod: {promo.code}",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        await state.clear()
    finally:
        db.close()
