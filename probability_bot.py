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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found! Make sure the .env file exists "
        "and contains BOT_TOKEN=your_token"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

class SetMaxStates(StatesGroup):
    waiting_for_max_num = State()


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
        "Пришли что угодно — скажу вероятность.\n"
        "Рекомендую воспользоваться командой /menu для комфортного пользования!\n\n"
        f"🇬🇧: Hello, {msg.from_user.first_name}! I am a Probability bot.\n" 
        "Send me anything — I will send probability."
        "I recommend use command /menu for comfortable use!",
        reply_markup=keyboard_for_start()
    )


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "🇷🇺: Это Probability бот. Я отвечу вероятность на твоё сообщение.\n\n"
        "🇬🇧: This is a Probability bot. I will calculate the probability for your message."
    )


@dp.message(Command("stats"))
async def cmd_stats(msg: Message, state: FSMContext):
    data = await state.get_data()
    count = data.get("count", 0)
    await msg.answer(
        f"🇷🇺: Ты отправил мне {count} сообщений.\n\n"
        f"🇬🇧: You have sent me {count} messages."
    )


@dp.message(Command("set"))
async def cmd_set(msg: Message, state: FSMContext):
    await msg.answer(
        "🇷🇺: Напиши число от 2 до 100 — это будет максимум вероятности.\n\n"
        "🇬🇧: Send a number from 2 to 100 — it will be the max probability."  
    )
    await state.set_state(SetMaxStates.waiting_for_max_num)


@dp.message(Command("menu"))
async def cmd_menu(msg: Message):
    await msg.answer(
        "🇷🇺: Выбери действие:\n"
        "/help  — узнать значение бота.\n"
        "/stats  — узнать сколько написал сообщений, где спрашивал вероятность.\n"
        "/set  — поменять максимальное число вероятности.\n"
        "🇬🇧: Choose an action:"
        "/help  — learn meaning bot.\n"
        "/stats  — learn how many wrote messages, where asked probability.\n"
        "/set  — change maximum number probability's.\n"
    )

@dp.message(SetMaxStates.waiting_for_max_num)
async def receive_max(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        await msg.answer(
            "🇷🇺: Это не число! Попробуй ещё раз.\n\n"
            "🇬🇧: That's not a number! Try again."
        )
        return

    max_value = int(msg.text)
    if not (2 <= max_value <= 100):
        await msg.answer(
            "🇷🇺: Число должно быть от 2 до 100!\n\n"
            "🇬🇧: The number must be between 2 and 100!"
        )
        return

    await state.update_data(max_value=max_value)
    await state.set_state(None)
    await msg.answer(
        f"🇷🇺: Готово! Теперь вероятности будут от 0 до {max_value}%.\n\n"
        f"🇬🇧: Done! Now probabilities go from 0 to {max_value}%."
    )


@dp.message()
async def probability(msg: Message, state: FSMContext):
    if msg.text:
        data = await state.get_data()
        count = data.get("count", 0)
        await state.update_data(count=count + 1)
        max_value = data.get("max_value", 100)

        num = random.randint(0, max_value)
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
async def try_again(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    max_value = data.get("max_value", 100)
    num = random.randint(0, max_value)
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