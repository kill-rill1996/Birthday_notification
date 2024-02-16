from typing import List
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

from database import services as db, tables



def create_user_key_board():
    """Клавиатура для старта создания профиля"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text="Создать аккаунт", callback_data="create_account")
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
    keyboard.row(
        InlineKeyboardButton(
            text="Отмена", callback_data="something_cancel"
        )
    )
    return keyboard


def admins_keyboard():
    """Клавиатура для администратора"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="События", callback_data="admin_events"),
        InlineKeyboardButton(
            text="Добавить событие", callback_data="admin_add-event"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Удаление польз.", callback_data="admin_delete-user"),
        InlineKeyboardButton(
            text="Удаление событий", callback_data="admin_delete-event"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Отмена", callback_data="something_cancel"
        )
    )
    return keyboard


def all_events_keyboard(events: List[tables.Event]):
    """Клавиатура администратора со всеми событиями"""
    keyboard = InlineKeyboardBuilder()
    for count, event in enumerate(events, start=1):
        event_user = db.get_user_by_id(event.user_id)  # получение пользователя из базы, иначе ошибка из-за дырявой базы
        if count % 2 == 1:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}",
                    callback_data=f"event_{event.id}"),
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}",
                    callback_data=f"event_{event.id}"),
            )

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_back"
        )
    )
    return keyboard

