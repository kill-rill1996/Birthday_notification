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
        text="Отмена", callback_data="cancel")
    )
    return keyboard