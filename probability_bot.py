import asyncio
import sys
import os
import random

from aiohttp import web

from dotenv import load_dotenv

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found! Make sure the .env file exists "
        "and contains BOT_TOKEN=your_token"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

def keyboard_for_else():
    second_builder = InlineKeyboardBuilder()
    second_builder.button(text="🇷🇺 Написать текст", callback_data="write_text")
    second_builder.button(text="🇬🇧 Write text", callback_data="write_text")
    second_builder.adjust(2)
    return second_builder.as_markup()


def keyboard_for_again():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Ещё раз", callback_data="try_again")
    builder.button(text="🇬🇧 Again", callback_data="try_again")
    builder.adjust(2)
    return builder.as_markup()


def keyboard_for_start():
    builder = InlineKeyboardBuilder()
    builder.button(text="GitHub", url="https://github.com/pavlov-developer")
    builder.adjust(1)
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        f"🇷🇺: Привет, {msg.from_user.first_name}! Я бот Вероятность.\n"
        "Пришли что угодно — скажу вероятность.\n\n"
        f"🇬🇧: Hello, {msg.from_user.first_name}! I am a Probability bot.\n" 
        "Send me anything — I will send probability.",
        reply_markup=keyboard_for_start()
    )


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "🇷🇺: Это Probability бот. Я отвечу вероятность на твоё сообщение.\n\n"
        "🇬🇧: This is a Probability bot. I will calculate the probability for your message."
    )


@dp.message()
async def probability(msg: Message):
    if msg.text:
        num = random.randint(0, 100)
        await msg.answer(
            f"🇷🇺: Я думаю, что вероятность этого {num}%!\n\n"
            f"🇬🇧: I think the probability of this is {num}%!",
            reply_markup=keyboard_for_again()
        )
    else:
        await msg.answer(
            "🇷🇺: Я принимаю только текстовые сообщения!\n\n"
            "🇬🇧: I only accept text messages!",
            reply_markup=keyboard_for_else()
        )


@dp.callback_query(F.data == "write_text")
async def write_text(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🇷🇺: Напиши что-нибудь — и я скажу вероятность.\n\n"
        "🇬🇧: Write something — and I'll tell you the probability."
    )


@dp.callback_query(F.data == "try_again")
async def try_again(callback: CallbackQuery):
    await callback.answer()
    num = random.randint(0, 100)
    try:
        await callback.message.edit_text(
            f"🇷🇺: Я думаю, что вероятность этого {num}%!\n\n"
            f"🇬🇧: I think the probability of this is {num}%!",
            reply_markup=keyboard_for_again()
        )
    except TelegramBadRequest:
        await callback.answer(
            "🇷🇺 Число не изменилось.\n\n"
            "🇬🇧 The number hasn't changed."
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