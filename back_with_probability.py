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

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()


class SetMaxStates(StatesGroup):
    waiting_for_max_num = State()


def keyboard_for_else():
    builder = InlineKeyboardBuilder()
    builder.button(text="Написать текст", callback_data="write_text")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_again():
    builder = InlineKeyboardBuilder()
    builder.button(text="Ещё раз", callback_data="try_again")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_start():
    builder = InlineKeyboardBuilder()
    builder.button(text="GitHub", url="https://github.com/pavlov-developer")
    builder.adjust(1)
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(msg: Message):
    await msg.answer(
        "u used start",
        reply_markup=keyboard_for_start()
    )


@dp.message(Command("stats"))
async def cmd_stats(msg: Message, state: FSMContext):
    data = await state.get_data()
    count = data.get("count", 0)
    await msg.answer(
        f"u sent {count} messages"
    )


@dp.message(Command("set"))
async def cmd_set(msg: Message, state: FSMContext):
    await msg.answer(
        "u will sent num from 2 to 100"
    )
    await state.set_state(SetMaxStates.waiting_for_max_num)


@dp.message(Command("menu"))
async def cmd_menu(msg: Message):
    await msg.answer(
        "u used menu"
    )

        
@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        "u used help"
    )


@dp.message(SetMaxStates.waiting_for_max_num)
async def receive_max(msg: Message, state: FSMContext):
    if not msg.text or not msg.text.isdigit():
        await msg.answer(
            "That's not a number!"
        )
        return

    max_value = int(msg.text)
    if not (2 <= max_value <= 100):
        await msg.answer(
            "Thu number must be between 2 and 100"
        )
        return

    await state.update_data(max_value=max_value)
    await state.set_state(None)
    await msg.answer(
        f"Now probabilities go from 2 and {max_value}"
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
            f"I think the probability of this is {max_value}%!",
            reply_markup=keyboard_for_again()
        )
    else:
        await msg.answer(
            "I only accept text messages!",
            reply_markup=keyboard_for_else()
        )


@dp.callback_query(F.data == "write_text")
async def try_again(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    


async def handle(request):
    return web.Response(text="Bot is running")


async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())