import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import router
import os
from dotenv import load_dotenv
from app.core.config import BASE_DIR

# .env faylini o'qib, muhit o'zgaruvchilariga qo'shish
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Bot tokenini atrof-muhit (.env) dan olish
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Asosiy ishga tushirish funksiyasi
async def main():
    # Bot obyektini yaratish
    bot = Bot(token=BOT_TOKEN)
    # Xabarlarni taqsimlovchi Dispatcher ni yaratish
    dp = Dispatcher()
    # Marshrutlarni (handlerlar) ulash
    dp.include_router(router)

    # Log yozish sozlamasi
    logging.basicConfig(level=logging.INFO)

    from aiogram.types import MenuButtonWebApp, WebAppInfo
    from bot.handlers import URL
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="🎮 O'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))
        )
        logging.info(f"Menu Button URL updated to {URL}/clicker")
    except Exception as e:
        logging.error(f"Failed to update menu button: {e}")

    # Oldingi eskirgan xabarlarni o'tkazib yuborish (Webhookni uchirish)
    await bot.delete_webhook(drop_pending_updates=True)
    # Botni ishga tushirish
    await dp.start_polling(bot)


# Dastur o'zi tomonidan chaqirilganda main qismini ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
