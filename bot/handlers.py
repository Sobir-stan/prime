from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.db.database import SessionLocal
from app.db import crud
import os

from app.db.models import Progress

router = Router()

URL = os.getenv("NGROK_URL", "http://localhost:8000")

class PromoStates(StatesGroup):
    waiting_for_promo = State()

def check_telegram_id(message: Message):
    is_registered = False
    with SessionLocal() as db:
        user = crud.get_user_by_telegram_id(db, message.from_user.id)
        is_registered = bool(user)
    return is_registered

def clicker_main_keyboard(message: Message):
    builder = InlineKeyboardBuilder()
    is_registered = check_telegram_id(message)
    target_url = f"{URL}/?tg_id={message.from_user.id}" if not is_registered else f"{URL}/clicker?tg_id={message.from_user.id}"
    builder.button(text="🎮 Clicker O'ynash", web_app=WebAppInfo(url=target_url))
    return builder.as_markup(resize_keyboard=True)

def get_main_keyboard(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🏆 Reyting")
    builder.button(text="💼 Vazifalar")
    builder.button(text="🎁 PROMOKOD")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Salom, {message.from_user.first_name}! Clicker o'yiniga xush kelibsiz.\n\n"
        "Mini App'ni ishga tushirish uchun 'Clicker O'ynash' tugmasini bosing.",
        reply_markup=get_main_keyboard(message)
    )
    await message.answer("🎮 Clicker o'ynash uchun quyidagi tugmani bosing:",
                         reply_markup=clicker_main_keyboard(message))

@router.message(F.text == "🏆 Reyting")
async def rating_handler(message: Message, state: FSMContext):
    await state.clear()
    with SessionLocal() as db:
        top = db.query(Progress).order_by(Progress.totalCookies.desc()).limit(10).all()
        if not top:
            await message.answer("Reyting hozircha bo'sh.")
            return
        response = "🏆 **TOP 10 O'yinchilar** 🏆\n\n"
        for i, p in enumerate(top, 1):
            response += f"{i}. {p.username} — {int(p.totalCookies)} ta pechenye\n"
        await message.answer(response, parse_mode="Markdown")

@router.message(F.text == "💼 Vazifalar")
async def tasks_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bu yerda vazifalar bo'ladi (masalan, kanallarga obuna bo'lish). Bu funksiya hali ishlab chiqilmoqda!")

@router.message(F.text == "🎁 PROMOKOD")
async def promo_code_button(message: Message, state: FSMContext):
    await state.set_state(PromoStates.waiting_for_promo)
    await message.answer("Iltimos Promokodni kiriting:")

@router.message(PromoStates.waiting_for_promo)
async def process_promo_code(message: Message, state: FSMContext):
    code = message.text.upper().strip()
    try:
        with SessionLocal() as db:
            with db.begin():
                user = crud.get_user_by_telegram_id(db, message.from_user.id)
                if not user:
                    await message.answer("❌ Avval '🎮 Clicker O'ynash' tugmasini bosing va akkauntingizni ulang!")
                    return

                username = user.username
                promo = crud.apply_promo_code_to_user(db, code, username)
                
                await message.answer(
                    f"✅ Tabriklaymiz! 🍪 {int(promo.cookies)} ta pechenye bonus sifatida {username} akkauntiga qo'shildi!\n\n"
                    "Bonus pechiniyani ko'rish uchun 'Clicker O'yini refresh qiling🔃",
                    reply_markup=get_main_keyboard(message)
                )
    except ValueError as e:
        await message.answer(f"❌ {str(e)}")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
    finally:
        await state.clear()
