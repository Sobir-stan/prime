from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from app.db.database import SessionLocal
from app.db.models import Progress

# Ushbu fayl aiogram orqali Telegram botning xabarlarini qayta ishlashni (handler) taminlaydi.
# Komandalar (/start), menyu tugmalari va WebApp havolasi shu faylda yaratiladi va sozlanadi.

router = Router()

# WebApp ga yo'naltiruvchi havola (Ngrok yoki sizning domeningiz)
URL = "https://ellie-ramulose-lajuana.ngrok-free.dev"

# Asosiy klaviatura (menyular) ni yaratish
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()

    # WebApp tugmasini qo'shish
    builder.button(text="🎮 Clicker O'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))
    builder.button(text="🏆 Reyting")
    builder.button(text="💼 Vazifalar")
    builder.button(text="🛒 Cookie Shop")
    # Tugmalarni ustun qilib joylash
    builder.adjust(2, 2)
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
    await message.answer("Bu yerda vazifalar bo'ladi (masalan, kanallarga obuna bo'lish). Bu funksiya hali ishlab chiqilmoqda!")


@router.message(F.text == "🛒 Cookie Shop")
async def shop_handler(message: Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🪙 Coin", callback_data="but_coin"),
                InlineKeyboardButton(text="🥚 Egg", callback_data="buy_egg"),
                InlineKeyboardButton(text="🍊 Orange", callback_data="buy_orange")
            ]
        ]
    )
    await message.answer("cookie shopdagi mahsulotlar ro'yxati va narxlari \n"
                         "1. Coin - 200 ta pechenye \n"
                         "2. Egg - 50 ta pechenye \n"
                         "3. Orange - 100 ta pechenye",
                         reply_markup=keyboard())


