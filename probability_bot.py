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


def keyboard_for_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Меню", callback_data="menu")
    builder.button(text="🇬🇧 Menu", callback_data="menu")
    builder.adjust(2)
    return builder.as_markup()


def keyboard_for_reset():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Сбросить режим", callback_data="reset_mode")
    builder.button(text="🇬🇧 Reset the mode", callback_data="reset_mode")
    builder.adjust(2)
    return builder.as_markup()


def keyboard_for_non_text_messages():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Написать текст", callback_data="write_text")
    builder.button(text="🇬🇧 Write text", callback_data="write_text")
    builder.adjust(2)
    return builder.as_markup()


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


def keyboard_for_set_language():
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺", callback_data="ru_language")
    builder.button(text="🇬🇧", callback_data="en_language")
    builder.adjust(2)
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    user_language = await db.get_language(msg.from_user.id)

    if user_language == "ru":
        lang_code = (msg.from_user.language_code or "").lower()
        if lang_code not in ("ru", "uk", "be", "kk", "kz"):
            user_language = "en"
            await db.set_language(msg.from_user.id, user_language)

    if user_language == "ru":
        await msg.answer(
            f"Привет, {msg.from_user.first_name}! Я бот Вероятность.\n"
            "Пришли что угодно — скажу вероятность.\n"
            "Используй /menu для комфортного пользования или /set_language для смены языка.\n\n",
            reply_markup=keyboard_for_start()
        )
    else:  
        await msg.answer(
            f"Hello, {msg.from_user.first_name}! I am a Probability bot.\n" 
            "Send me anything — I will calculate the probability.\n"
            "Use /menu command for a better experience or /set_language to change language",
            reply_markup=keyboard_for_start()
        )


@dp.message(Command("help"))
async def cmd_help(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
            "Это Probability бот. Я отвечу вероятность на твоё сообщение."
        )
    else:
        await msg.answer(
            "This is a Probability bot. I will calculate the probability for your message."
        )


@dp.message(Command("stats"))
async def cmd_stats(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    count, _ = await db.get_users_stats(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
            f"Ты отправил мне {count} сообщений."
        )
    else:
        await msg.answer(
            f"You have sent me {count} messages."
        )


@dp.message(Command("set"))
async def cmd_set(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
        "Напиши число от 2 до 100 — это будет максимум вероятности.\n"
        "Если передумал, просто напиши 100 (сброс по умолчанию)."
        )
    else:
        await msg.answer(
            "Send a number from 2 to 100 — it will be the max probability.\n"
            "If you changed your mind, just send 100 (reset to default)."
        )
    
    await state.set_state(SetStates.waiting_for_max_num)


@dp.message(Command("set_language"))
async def set_language(msg: Message):
    await msg.answer(
        "Выбери язык",
        reply_markup=keyboard_for_set_language()
    )


@dp.message(Command("echo"))
async def cmd_echo(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
            "🇷🇺: Готово! Теперь стоит эхо режим.\n"
            "Если хотите вернуться в режим вероятности — нажмите кнопку сброса режима.",
            reply_markup=keyboard_for_reset()
        )
    else:
        await msg.answer(
            "Done! The echo mode is now enabled.\n"
            "If you want to return to the probabilistic mode, press the mode reset button.",
            reply_markup=keyboard_for_reset()
        )
    
    await state.set_state(SetStates.waiting_for_echo)


@dp.message(Command("yes_or_no"))
async def cmd_yes_or_no(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
            "Готово! Теперь стоит режим Да/Нет.\n"
            "Если хотите вернуться в режим вероятности — нажмите кнопку сброса режима.",
            reply_markup=keyboard_for_reset()
        )
    else:
        await msg.answer(
            "🇬🇧: Done! The Yes/No mode is now enabled.\n"
            "If you want to return to the probabilistic mode, press the mode reset button.",
            reply_markup=keyboard_for_reset()
        )
    
    await state.set_state(SetStates.waiting_for_yes_or_no)


@dp.message(Command("menu"))
async def cmd_menu(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if language == "ru":
        await msg.answer(
            "Выбери действие:\n"
            "/help  — узнать, что делает бот.\n"
            "/stats  — узнать сколько сообщений ты отправил.\n"
            "/set  — поменять максимальное число вероятности.\n"
            "/echo — для режима эхо.\n"
            "/yes_or_no — для режима Да/Нет.\n"
            "/set_language — сменить язык (ru/en)."
        )
    else:
        await msg.answer(
            "Choose an action:\n"
            "/help  — learn what the bot does.\n"
            "/stats  — see how many messages you've sent.\n"
            "/set  — change the maximum number probability limit.\n"
            "/echo — for echo mode.\n"
            "/yes_or_no — for Yes/No mode.\n"
            "/set_language — change language (ru/en)."
        )


@dp.message(SetStates.waiting_for_max_num)
async def receive_max(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)

    if not msg.text or not msg.text.isdigit():
        if language == "ru":
            await msg.answer(
                "Это не число! Попробуй ещё раз."
            )
        else:
            await msg.answer(
                "That's not a number! Try again."
            )
        return

    max_value = int(msg.text)
    if not (2 <= max_value <= 100):
        if language == "ru":
            await msg.answer(
                "Число должно быть от 2 до 100!"
            )
        else:
            await msg.answer(
                "The number must be between 2 and 100!"
            )
        return

    await db.set_max_value(msg.from_user.id, max_value)

    await state.set_state(None)

    if language == "ru":
        await msg.answer(
            f"Готово! Теперь вероятности будут от 0 до {max_value}%."
        )
    else:
        await msg.answer(
            f"Done! Now probabilities go from 0 to {max_value}%."
        )


@dp.message(SetStates.waiting_for_echo)
async def echo(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if msg.text:
        await msg.answer(msg.text)
    else:
        if language == "ru":
            await msg.answer(
                "Я принимаю только текстовые сообщения!",
                reply_markup=keyboard_for_reset()
            )
        else:
            await msg.answer(
                "I only accept text messages!",
                reply_markup=keyboard_for_reset()
            )


@dp.message(SetStates.waiting_for_yes_or_no)
async def yes_or_no(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if msg.text:
        choice = random.choice(["positive", "negative"])
        if choice == "positive":
            if language == "ru":
                await msg.answer(
                    "Да."
                )
            else:
                await msg.answer(
                    "Yes."
                )
        elif choice == "negative":
            if language == "ru":
                await msg.answer(
                    "Нет."
                )
            else:
                await msg.answer(
                    "No."
                )
    else:
        if language == "ru":
            await msg.answer(
                "Я принимаю только текстовые сообщения!",
                reply_markup=keyboard_for_reset()
            )
        else:
            await msg.answer(
                "I only accept text messages!",
                reply_markup=keyboard_for_reset()
            )


@dp.callback_query(F.data == "ru_language")
async def change_language_ru(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "ru")

    await callback.message.answer("Язык изменён на русский!")


@dp.callback_query(F.data == "en_language")
async def change_language_en(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "en")

    await callback.message.answer("Language changed to English!")


@dp.message()
async def probability(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)
 
    language = await db.get_language(msg.from_user.id)

    if msg.text:
        await db.increment_count(msg.from_user.id)
        _, max_value = await db.get_users_stats(msg.from_user.id)
        num = random.randint(0, max_value)

        if language == "ru":
            await msg.answer(
                f"Я думаю, что вероятность этого {num}%!",
                reply_markup=keyboard_for_again()
            )
        else:
            await msg.answer(
                f"I think the probability of this is {num}%!",
                reply_markup=keyboard_for_again()
            )
    else:
        if language == "ru":
            await msg.answer(
                "Я принимаю только текстовые сообщения!",
                reply_markup=keyboard_for_non_text_messages()
            )
        else:
            await msg.answer(
                "I only accept text messages!",
                reply_markup=keyboard_for_non_text_messages()
            )


@dp.callback_query(F.data == "write_text")
async def write_text(callback: CallbackQuery, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    if language == "ru":
        await callback.message.answer(
            "Напиши что-нибудь — и я скажу вероятность."
        )
    else:
        await callback.message.answer(
            "Write something — and I'll tell you the probability."
        )


@dp.callback_query(F.data == "try_again")
async def try_again(callback: CallbackQuery, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    _, max_value = await db.get_users_stats(callback.from_user.id)
    
    num = random.randint(0, max_value)
    try:
        if language == "ru":
            await callback.message.edit_text(
                f"Я думаю, что вероятность этого {num}%!",
                reply_markup=keyboard_for_again()
            )
        else:
            await callback.message.edit_text(
                f"I think the probability of this is {num}%!",
                reply_markup=keyboard_for_again()
            )
    except TelegramBadRequest:
        if language == "ru":
            await callback.answer(
                "Число не изменилось."
            )
        else:
            await callback.answer(
                "The number hasn't changed."
            )


@dp.callback_query(F.data == "reset_mode")
async def reset_mode(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)

    if language == "ru":
        await callback.message.answer(
            "Режим сброшен! Нажми на кнопку чтобы появилось меню.",
            reply_markup=keyboard_for_menu()
        )
    else:
        await callback.message.answer(
            "Mode reset! Click the button to open the menu.",
            reply_markup=keyboard_for_menu()
        )


@dp.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()
    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)

    if language == "ru":
        await callback.message.answer(
            "Выбери действие:\n"
            "/help  — узнать, что делает бот.\n"
            "/stats  — узнать сколько сообщений ты отправил.\n"
            "/set  — поменять максимальное число вероятности.\n"
            "/echo — для режима эхо.\n"
            "/yes_or_no — для режима Да/Нет.\n"
            "/set_language — сменить язык (ru/en)."
        )
    else:
        await callback.message.answer(
            "Choose an action:\n"
            "/help  — learn what the bot does.\n"
            "/stats  — see how many messages you've sent.\n"
            "/set  — change the maximum number probability limit.\n"
            "/echo — for echo mode.\n"
            "/yes_or_no — for Yes/No mode.\n"
            "/set_language — change language (ru/en)."
        )


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