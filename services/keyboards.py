from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import SALT as s


def create_user_key_board():
    """Клавиатура для старта создания профиля"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text="Создать аккаунт", callback_data="Создать аккаунт")
    )
    return keyboard


def cancel_inline_keyboard():
    """Клавиатура для отмены"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text="Отмена", callback_data="something_cancel")
    )
    return keyboard


def yes_no_keyboard():
    """Клавиатура для подтверждения действия"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Да", callback_data="yes_delete"),
        InlineKeyboardButton(
            text="Нет", callback_data="no_delete"
        )
    )
    return keyboard


def update_profile_keyboard():
    """Клавиатура для обновления профиля"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Имя", callback_data="name_update"),
        InlineKeyboardButton(
            text="Дата рождения", callback_data="date_update"
        )
    )
    return keyboard