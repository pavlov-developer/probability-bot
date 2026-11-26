import asyncio
import sys
import os

from dotenv import load_dotenv

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from aiogram import Bot, Dispatcher

from database import DataBase
from handlers import callbacks, commands, modes

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
    db = DataBase()

    await db.connect()
    await db.init_db()

    dp["db"] = db

    dp.include_router(modes.router)
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())