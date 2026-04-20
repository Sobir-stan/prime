import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from bot.handlers import router
from dotenv import load_dotenv
from app.core.config import BASE_DIR

# Load .env
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Configure logging to console and file so we can inspect why the bot stops
LOG_FILE = BASE_DIR / "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Put it into .env or environment and restart.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Try to set menu button (non-fatal)
    try:
        from aiogram.types import MenuButtonWebApp, WebAppInfo
        from bot.handlers import URL
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="🎮 O'ynash", web_app=WebAppInfo(url=f"{URL}/clicker"))
        )
        logger.info(f"Menu Button URL updated to {URL}/clicker")
    except Exception as e:
        logger.warning(f"Failed to update menu button: {e}")

    # ensure webhook removed
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        logger.exception("Failed to delete webhook (continuing)")

    # Run polling in a resilient loop with backoff so transient errors won't stop the process
    backoff = 5
    max_backoff = 300
    while True:
        try:
            logger.info("Starting polling...")
            await dp.start_polling(bot)
            logger.info("Dispatcher polling finished normally. Exiting loop.")
            break
        except Exception:
            logger.exception(f"Polling failed. Restarting in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(max_backoff, int(backoff * 1.5))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
