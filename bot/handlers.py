from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.db.database import SessionLocal
from app.db import crud
import os

# WebApp ga yo'naltiruvchi havola (Ngrok avtomatik tarzda sozlanadi)
URL = os.getenv("NGROK_URL", "https://stan.uz")

"""Minimal bot handlers for managing running news messages.

Supported command(s):
  /yangiliklar        - list existing active news

This file now exposes only the listing handler as requested.
"""

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    """Send an inline WebApp button that opens the clicker web page.

    Label: Clicker o'ynash
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Clicker o'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))]
    ])

    await message.reply("Clickerga xush kelibsiz! Quyidagi tugmani bosing:", reply_markup=kb)


@router.message(Command("link_admin"))
async def link_admin_handler(message: Message):
    """Link the sender Telegram ID to the web 'admin' user record.

    This command can only be used by Telegram accounts listed in ADMIN_IDS env var.
    """
    user_id = getattr(message.from_user, 'id', None)
    admin_ids_env = os.getenv('ADMIN_IDS', '')
    admin_ids = set()
    if admin_ids_env:
        for part in admin_ids_env.split(','):
            try:
                admin_ids.add(int(part.strip()))
            except Exception:
                pass

    if user_id not in admin_ids:
        await message.reply("Siz admin emassiz yoki ruxsatnoma topilmadi.")
        return

    db = SessionLocal()
    try:
        admin_user = crud.get_user_by_username(db, 'admin')
        if not admin_user:
            await message.reply("Web tizimida 'admin' foydalanuvchisi topilmadi.")
            return

        admin_user.telegram_id = user_id
        db.commit()
        await message.reply(f"Admin Telegram ID ({user_id}) bazaga saqlandi.")
    finally:
        db.close()


@router.message(Command("yangiliklar"))
async def yangiliklar_handler(message: Message):
    db = SessionLocal()
    try:
        # Determine if the Telegram user is an admin by Telegram user id.
        # Set ADMIN_IDS environment variable to a comma-separated list of admin user ids (e.g. "12345,67890").
        user_id = getattr(message.from_user, 'id', None)
        admin_ids_env = os.getenv('ADMIN_IDS', '')
        admin_ids = set()
        if admin_ids_env:
            for part in admin_ids_env.split(','):
                try:
                    admin_ids.add(int(part.strip()))
                except Exception:
                    pass
        is_admin = (user_id in admin_ids)
        username = getattr(message.from_user, 'username', None)
        if username:
            uname_line = f"Username: @{username} (ID: {user_id})"
        else:
            uname_line = "Bunday foydalanuvchi yoq"

        if is_admin:
            admin_note = f"{uname_line}\n\nsiz admin akkaunti orqali kirgansiz"
        else:
            # For non-admins show username (with id) or the 'not found' message
            admin_note = uname_line

        # Only show active messages to users of /yangiliklar
        items = crud.list_news(db)
        active = [n for n in items if getattr(n, 'active', False)]
        if not active:
            await message.reply(f"{admin_note}\n\nHozircha hech qanday faol yangilik yo'q.")
            return

        text = f"{admin_note}\n\n📣 Yuguruvchi yangiliklar (faol):\n\n"
        for n in active:
            # show id and timestamp and a short preview
            short = (n.text[:120] + '...') if len(n.text) > 120 else n.text
            text += f"#{n.id} ({n.created_at})\n{short}\n\n"

        text += "Foydalanish: /yangiliklar\n"
        await message.reply(text)
    finally:
        db.close()


@router.message(Command("status"))
async def status_handler(message: Message):
    """Simple liveness check from Telegram to see if bot is responsive."""
    try:
        await message.reply("Bot is running ✅")
    except Exception as e:
        # best-effort reply; if it fails, just raise so aiogram logs it
        raise

