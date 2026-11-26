import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram.utils.keyboard import InlineKeyboardBuilder
from texts import TEXTS


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