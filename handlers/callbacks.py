import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from database import DataBase
from texts import TEXTS
from handlers.keyboards import (
    keyboard_for_menu,
    keyboard_for_again,
    keyboard_for_non_text_messages,
    keyboard_for_reset
)

router = Router()


@router.callback_query(F.data == "ru_language")
async def change_language_ru(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "ru")

    await callback.message.answer(
        TEXTS["ru"]["lang_changed"]
    )


@router.callback_query(F.data == "en_language")
async def change_language_en(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    await db.set_language(callback.from_user.id, "en")

    await callback.message.answer(
        TEXTS["en"]["lang_changed"]
    )


@router.callback_query(F.data == "write_text")
async def write_text(callback: CallbackQuery, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await callback.message.answer(
        TEXTS[language]["write_text_prompt"],
        reply_markup=keyboard_for_reset(language)
    )


@router.callback_query(F.data == "try_again")
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
        await callback.answer(
            TEXTS[language]["number_not_changed"]
        )


@router.callback_query(F.data == "reset_mode")
async def reset_mode(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)

    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)
    await callback.message.answer(
        TEXTS[language]["mode_reset"],
        reply_markup=keyboard_for_menu(language)
    )


@router.callback_query(F.data == "menu")
async def menu(callback: CallbackQuery, state: FSMContext, db: DataBase):
    await callback.answer()

    await db.ensure_user(callback.from_user.id)
    language = await db.get_language(callback.from_user.id)

    await state.set_state(None)
    
    await callback.message.answer(
        TEXTS[language]["menu"]
    )