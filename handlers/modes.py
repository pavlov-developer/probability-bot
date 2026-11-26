import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import DataBase
from texts import TEXTS
from states import SetStates
from handlers.keyboards import keyboard_for_reset, keyboard_for_non_text_messages

router = Router()


@router.message(SetStates.waiting_for_max_num)
async def receive_max(msg: Message, state: FSMContext, db: DataBase):
    await db.ensure_user(msg.from_user.id)

    language = await db.get_language(msg.from_user.id)

    if not msg.text or not msg.text.isdigit():
        await msg.answer(
            TEXTS[language]["not_number"]
        )
        return

    max_value = int(msg.text)
    if not (2 <= max_value <= 100):
        await msg.answer(
            TEXTS[language]["invalid_range"]
        )
        return

    await db.set_max_value(msg.from_user.id, max_value)
    await state.set_state(None)
    await msg.answer(
        TEXTS[language]["max_changed"].format(max_value=max_value)
    )


@router.message(SetStates.waiting_for_echo)
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


@router.message(SetStates.waiting_for_yes_or_no)
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