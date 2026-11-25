import asyncio
import sys
import os
import random

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

from database import DataBase
from texts import TEXTS

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError(
        "Token not found! Make sure the .env file exists "
        "and contains BOT_TOKEN=your_token"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

class SetStates(StatesGroup):
    waiting_for_max_num = State()
    waiting_for_echo = State()
    waiting_for_yes_or_no = State()
    

def keyboard_for_menu(language: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=TEXTS[language]["btn_menu"], callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_reset(language: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=TEXTS[language]["btn_reset"], callback_data="reset_mode")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_non_text_messages(language: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=TEXTS[language]["btn_write"], callback_data="write_text")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_again(language: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=TEXTS[language]["btn_again"], callback_data="try_again")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_start():
    builder = InlineKeyboardBuilder()
    builder.button(text="GitHub", url="https://github.com/pavlov-developer")
    builder.adjust(1)
    return builder.as_markup()


def keyboard_for_set_language():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺", callback_data="ru_language")
    builder.button(text="🇬🇧", callback_data="en_language")
    builder.adjust(2)
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(msg: Message, db: DataBase):
    is_new_user = await db.ensure_user(msg.from_user.id)

    if is_new_user:
        lang_code = (msg.from_user.language_code or "").lower()
        if lang_code in ("ru", "uk", "be", "kk", "kz"):
            user_language = "ru"
        else:
            user_language = "en"
        await db.set_language(msg.from_user.id, user_language)
    else:
        user_language = await db.get_language(msg.from_user.id)    

    name = msg.from_user.first_name or TEXTS[user_language]["default_name"]

    await msg.answer(
        TEXTS[user_language]["start"].format(name=name),
        reply_markup=keyboard_for_start()
    )


@dp.message(Command("help"))
async def cmd_help(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(TEXTS[language]["help"])


@dp.message(Command("stats"))
async def cmd_stats(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    count, _ = await db.get_users_stats(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)

    await msg.answer(TEXTS[language]["stats"].format(count=count))


@dp.message(Command("set"))
async def cmd_set(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(TEXTS[language]["set_number"])
    
    await state.set_state(SetStates.waiting_for_max_num)


@dp.message(Command("set_language"))
async def set_language(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(
        TEXTS[language]["set_language"],
        reply_markup=keyboard_for_set_language()
    )


@dp.message(Command("echo"))
async def cmd_echo(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    text = TEXTS[language]["echo_mode_on"] + "\n" + TEXTS[language]["return_to_probability_hint"]
    await msg.answer(text, reply_markup=keyboard_for_reset(language))
    
    await state.set_state(SetStates.waiting_for_echo)


@dp.message(Command("yes_or_no"))
async def cmd_yes_or_no(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    text = TEXTS[language]["yes_or_no_mode_on"] + "\n" + TEXTS[language]["return_to_probability_hint"]
    await msg.answer(text, reply_markup=keyboard_for_reset(language))
    
    await state.set_state(SetStates.waiting_for_yes_or_no)


@dp.message(Command("menu"))
async def cmd_menu(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(TEXTS[language]["menu"])


@dp.message(SetStates.waiting_for_max_num)
async def receive_max(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)

    if not msg.text or not msg.text.isdigit():
        await msg.answer(TEXTS[language]["not_number"])
        return

    max_value = int(msg.text)
    if not (2 <= max_value <= 100):
        await msg.answer(TEXTS[language]["invalid_range"])
        return

    await db.set_max_value(msg.from_user.id, max_value)

    await state.set_state(None)

    await msg.answer(TEXTS[language]["max_changed"].format(max_value=max_value))


@dp.message(SetStates.waiting_for_echo)
async def echo(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if msg.text:
        await msg.answer(
            msg.text,
            reply_markup=keyboard_for_reset(language)
        )
    else:
        await msg.answer(
            TEXTS[language]["text_only"],
            reply_markup=keyboard_for_non_text_messages(language)
        )


@dp.message(SetStates.waiting_for_yes_or_no)
async def yes_or_no(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if msg.text:
        choice = random.choice(["positive", "negative"])

        if choice == "positive":
            await msg.answer(
                TEXTS[language]["yes"],
                reply_markup=keyboard_for_reset(language)
            )
        
        elif choice == "negative":
            await msg.answer(
                TEXTS[language]["no"],
                reply_markup=keyboard_for_reset(language)
            )
    else:
        await msg.answer(
            TEXTS[language]["text_only"],
            reply_markup=keyboard_for_non_text_messages(language)
        )
        

@dp.callback_query(F.data == "ru_language")
async def change_language_ru(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "ru")

    await callback.message.answer(TEXTS["ru"]["lang_changed"])


@dp.callback_query(F.data == "en_language")
async def change_language_en(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "en")

    await callback.message.answer(TEXTS["en"]["lang_changed"])


@dp.message()
async def probability(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)
 
    language = await db.get_language(msg.from_user.id)

    if msg.text:
        await db.increment_count(msg.from_user.id)
        _, max_value = await db.get_users_stats(msg.from_user.id)
        num = random.randint(0, max_value)

        await msg.answer(
                TEXTS[language]["probability"].format(num=num),
                reply_markup=keyboard_for_again(language)
            )
    else:
        await msg.answer(
            TEXTS[language]["text_only"],
            reply_markup=keyboard_for_non_text_messages(language)
        )


@dp.callback_query(F.data == "write_text")
async def write_text(callback: CallbackQuery, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await callback.message.answer(TEXTS[language]["write_text_prompt"])


@dp.callback_query(F.data == "try_again")
async def try_again(callback: CallbackQuery, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    _, max_value = await db.get_users_stats(callback.from_user.id)
    
    num = random.randint(0, max_value)
    try:
        await callback.message.edit_text(
            TEXTS[language]["probability"].format(num=num),
            reply_markup=keyboard_for_again(language)
        )
    except TelegramBadRequest:
        await callback.answer(TEXTS[language]["number_not_changed"])


@dp.callback_query(F.data == "reset_mode")
async def reset_mode(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)

    await callback.message.answer(
        TEXTS[language]["mode_reset"],
        reply_markup=keyboard_for_menu(language)
    )


@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)

    await callback.message.answer(TEXTS[language]["menu"])


async def main():
    db = DataBase()

    await db.connect()
    await db.init_db()

    dp["db"] = db

    try:
        await dp.start_polling(bot)
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())