import asyncio
import sys
import os
import random

from aiohttp import web

from dotenv import load_dotenv

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found! Make sure the .env file exists "
        "and contains BOT_TOKEN=your_token"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        f"🇷🇺: Привет, {msg.from_user.first_name}! Я бот Да/Нет.\n"
        "Пришли что угодно — отвечу Да/Нет.\n\n"
        f"🇬🇧: Hello, {msg.from_user.first_name}! I am a Yes/No bot.\n" 
        "Send me anything — I will send Yes/No."
    )


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "🇷🇺: Это Да/Нет бот. Я отвечу Да или Нет на твоё сообщение.\n\n"
        "🇬🇧: This is a Yes/No bot. I will answer Yes or No on your message."
    )


@dp.message()
async def yes_or_no(msg: Message):
    if msg.text:
        choice = random.choice(["positive", "negative"])
        if choice == "positive":
            await msg.answer(
                "🇷🇺: Да.\n\n"
                "🇬🇧: Yes."
            )
        elif choice == "negative":
            await msg.answer(
                "🇷🇺: Нет.\n\n"
                "🇬🇧: No."
            )
    else:
        await msg.answer(
            "🇷🇺: Я принимаю только текстовые сообщения!\n\n"
            "🇬🇧: I only accept text messages!"
        )


async def handle(request):
    return web.Response(text="Bot is running")


async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

    print("Bot is started and ready to work")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())