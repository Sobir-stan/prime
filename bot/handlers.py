from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.db.database import SessionLocal
from app.db import crud
import os

# WebApp ga yo'naltiruvchi havola (Ngrok avtomatik tarzda sozlanadi)
URL = os.getenv("NGROK_URL", "https://stan.uz")

"""Minimal bot handlers for managing running news messages.

Supported commands:
  /yangiliklar        - list existing news and show usage
  /add <text>         - add a new news message (active by default)
  /activate <id>      - mark news active
  /deactivate <id>    - mark news inactive
  /delete <id>        - delete specific news
  /delete_all         - delete all news

This file intentionally keeps only the news-related handlers per your request.
"""

router = Router()


@router.message(Command("yangiliklar"))
async def yangiliklar_handler(message: Message):
    db = SessionLocal()
    try:
        # Only show active messages to users of /yangiliklar
        items = crud.list_news(db)
        active = [n for n in items if getattr(n, 'active', False)]
        if not active:
            await message.reply("Hozircha hech qanday faol yangilik yo'q.")
            return

        text = "📣 Yuguruvchi yangiliklar (faol):\n\n"
        for n in active:
            # show id and timestamp and a short preview
            short = (n.text[:120] + '...') if len(n.text) > 120 else n.text
            text += f"#{n.id} ({n.created_at})\n{short}\n\n"

        text += "Foydalanish: /add <text> , /deactivate <id>, /activate <id>, /delete <id>, /delete_all\n"
        await message.reply(text)
    finally:
        db.close()


@router.message(Command("add"))
async def add_handler(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await message.reply("Iltimos xabar matnini kiriting: /add <matn>")
        return
    text = parts[1].strip()
    db = SessionLocal()
    try:
        n = crud.create_news(db, text)
        await message.reply(f"Qo'shildi ✅ #{n.id}")
    finally:
        db.close()


async def _parse_id_arg(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None, 'Iltimos id kiriting: /<command> <id>'
    try:
        return int(parts[1].strip()), None
    except ValueError:
        return None, 'Id butun son bolishi kerak.'


@router.message(Command("activate"))
async def activate_handler(message: Message):
    nid, err = await _parse_id_arg(message)
    if err:
        await message.reply(err)
        return
    db = SessionLocal()
    try:
        ok = crud.set_news_active(db, nid, True)
        if ok:
            await message.reply(f"# {nid} ✅ activated")
        else:
            await message.reply("Yangilik topilmadi.")
    finally:
        db.close()


@router.message(Command("deactivate"))
async def deactivate_handler(message: Message):
    nid, err = await _parse_id_arg(message)
    if err:
        await message.reply(err)
        return
    db = SessionLocal()
    try:
        ok = crud.set_news_active(db, nid, False)
        if ok:
            await message.reply(f"# {nid} ⛔ deactivated")
        else:
            await message.reply("Yangilik topilmadi.")
    finally:
        db.close()


@router.message(Command("delete"))
async def delete_handler(message: Message):
    nid, err = await _parse_id_arg(message)
    if err:
        await message.reply(err)
        return
    db = SessionLocal()
    try:
        ok = crud.delete_news(db, nid)
        if ok:
            await message.reply(f"# {nid} 🗑️ deleted")
        else:
            await message.reply("Yangilik topilmadi.")
    finally:
        db.close()


@router.message(Command("delete_all"))
async def delete_all_handler(message: Message):
    db = SessionLocal()
    try:
        crud.delete_all_news(db)
        await message.reply("Barcha yangiliklar o'chirildi.")
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

