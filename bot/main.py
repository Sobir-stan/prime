import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers import router
import os
from app.core.config import BASE_DIR

# Ushbu fayl Telegram botni ishga tushiruvchi asosiy fayl hisoblanadi.
# U Dispatcherni va botni sozlaydi va doimiy tarzda xabarlarni eshitib turish (polling) uchun ishlatiladi.

# Bot tokenini atrof-muhit (.env) dan olish
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)

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
    # Oldingi eskirgan xabarlarni o'tkazib yuborish (Webhookni uchirish)
    await bot.delete_webhook(drop_pending_updates=True)
    # Botni ishga tushirish
    await dp.start_polling(bot)

# Dastur o'zi tomonidan chaqirilganda main qismini ishga tushirish
if __name__ == "__main__":
    asyncio.run(main())
