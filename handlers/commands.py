import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import DataBase
from texts import TEXTS
from handlers.keyboards import keyboard_for_start, keyboard_for_set_language, keyboard_for_reset
from states import SetStates

router = Router()


@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext, db: DataBase):
    await state.set_state(None)

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


@router.message(Command("help"))
async def cmd_help(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(
        TEXTS[language]["help"]
    )


@router.message(Command("stats"))
async def cmd_stats(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    count, _ = await db.get_users_stats(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)
    await msg.answer(
        TEXTS[language]["stats"].format(count=count)
    )


@router.message(Command("set"))
async def cmd_set(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(
        TEXTS[language]["set_number"]
    )

    await state.set_state(SetStates.waiting_for_max_num)


@router.message(Command("set_language"))
async def set_language(msg: Message, db: DataBase):
    await db.ensure_user(msg.from_user.id)
    language = await db.get_language(msg.from_user.id)

    await msg.answer(
        TEXTS[language]["set_language"],
        reply_markup=keyboard_for_set_language()
    )


@router.message(Command("echo"))
async def cmd_echo(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    text = TEXTS[language]["echo_mode_on"] + "\n" + TEXTS[language]["return_to_probability_hint"]
    await msg.answer(
        text,
        reply_markup=keyboard_for_reset(language)
    )

    await state.set_state(SetStates.waiting_for_echo)


@router.message(Command("yes_or_no"))
async def cmd_yes_or_no(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    text = TEXTS[language]["yes_or_no_mode_on"] + "\n" + TEXTS[language]["return_to_probability_hint"]
    await msg.answer(
        text,
        reply_markup=keyboard_for_reset(language)
    )

    await state.set_state(SetStates.waiting_for_yes_or_no)


@router.message(Command("menu"))
async def cmd_menu(msg: Message, state: FSMContext, db: DataBase):
    await state.set_state(None)

    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    await msg.answer(
        TEXTS[language]["menu"]
    )