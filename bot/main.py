import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import router
import os
from app.core.config import BASE_DIR

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    # Xabarlarni taqsimlovchi Dispatcher ni yaratish
    dp = Dispatcher(storage=storage)
    # Marshrutlarni (handlerlar) ulash
    dp.include_router(router)

    # Log yozish sozlamasi
    logging.basicConfig(level=logging.INFO)
    # Oldingi eskirgan xabarlarni o'tkazib yuborish (Webhookni uchirish)
    await bot.delete_webhook(drop_pending_updates=True)
    # Botni ishga tushirish
    await dp.start_polling(bot)

# Dastur o'zi tomonidan chaqirilganda main qismini ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
