import asyncio
import sys
import os
import logging

from dotenv import load_dotenv

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from aiogram import Bot, Dispatcher

from database import DataBase
from handlers import callbacks, commands, modes
from handlers.middleware import ErrorLoggingMiddleware

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found! Make sure the .env file exists "
        "and contains BOT_TOKEN=your_token"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    logger.info("=== Bot starting ===")

    db = DataBase()

    await db.connect()
    logger.info("=== Database connected ===")

    await db.init_db()
    logger.info("=== Database tables initialized ===")

    dp["db"] = db

    dp.message.middleware(ErrorLoggingMiddleware())
    dp.callback_query.middleware(ErrorLoggingMiddleware())

    dp.include_router(modes.router)
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    logger.info("=== Routers connected ===")

    try:
        logger.info("=== Starting polling ===")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
    finally:
        await db.close()
        logger.info("=== Bot stopped ===")


if __name__ == "__main__":
    asyncio.run(main())