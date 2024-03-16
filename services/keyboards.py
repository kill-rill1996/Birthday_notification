from typing import List, Union
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

import config
from config import PAID1, PAID2, PAID3

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
            text="Пользователи", callback_data="admin_users"),
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Добавить событие", callback_data="admin_add-event"
        ),
        InlineKeyboardButton(
            text="Удалить польз.", callback_data="admin_delete-user"),
    )

    keyboard.row(
        InlineKeyboardButton(
            text="Удалить событие", callback_data="admin_delete-event"
        ),
        InlineKeyboardButton(
            text="Оповещения", callback_data="admin_ping"),
    )
    return keyboard


def all_events_keyboard(events: List[tables.Event]):
    """Клавиатура администратора со всеми событиями"""
    keyboard = InlineKeyboardBuilder()

    for event in events:
        if event.title == "birthday":
            event_user = db.get_user_by_id(event.user_id)
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}",
                    callback_data=f"event_{event.id}"),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event.title}",
                    callback_data=f"event_{event.id}"),
            )
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_back"
        )
    )
    return keyboard


def all_users_keyboard_to_delete(users: List[tables.User]):
    """Клавиатура всех пользователей для администратора"""
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{user.user_name} {datetime.strftime(user.birthday_date, '%d.%m.%Y')} ",
                callback_data=f"user-delete_{user.id}"),
        )
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_back"
        )
    )
    return keyboard


def yes_no_admin_keyboard(param: Union[int, str]):
    """Клавиатура для подтверждения действия от администратора"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="Да", callback_data=f"yes_{param}"),
        InlineKeyboardButton(
            text="Нет", callback_data=f"no_{param}"
        )
    )
    return keyboard


def back_admin_keyboard():
    """Клавиатура администратора для возвращения назад"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_back"
        )
    )
    return keyboard


def payer_info_admin_keyboard(event: tables.Event, payer_users: List[tables.User]):
    """Клаивиатура администратора для просмотра оплаты конкретным пользователем"""
    keyboard = InlineKeyboardBuilder()

    for payer in event.payers:
        for user in payer_users:
            if payer.user_id == user.id:
                if not payer.payment_status:
                    keyboard.add(InlineKeyboardButton(
                        text=f"{user.user_name}",
                        callback_data=f"admin-payer_{payer.id}"
                    ))

    keyboard.adjust(2)

    if event.title != "birthday":
        keyboard.row(
            InlineKeyboardButton(
                text="Изменить название события>>",
                callback_data=f"update-event-title_{event.id}"
            )
        )

    keyboard.row(
        InlineKeyboardButton(
            text="Изменить дату события>>",
            callback_data=f"update-event-date_{event.id}"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            text="Изменить телефон для события>>",
            callback_data=f"update-event-phone_{event.id}"
        )
    )

    keyboard.row(InlineKeyboardButton(
            text="<<Назад",
            callback_data="admin_events"
        )
    )

    return keyboard


def add_payment_admin_keyboard(payer_id: int, event_id: int):
    """Клавиатура для добавления оплаты пользователем"""
    keyboard = InlineKeyboardBuilder()

    keyboard.row(InlineKeyboardButton(
        text="Внести оплату",
        callback_data=f"add-pay_{payer_id}"
    ))

    keyboard.row(InlineKeyboardButton(
            text="<<Назад",
            callback_data=f"event_{event_id}"
        )
    )
    return keyboard


def add_event_admin_keyboard():
    """Клавиатура для создания событий от лица администратора"""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text="День рождения",
            callback_data=f"add-event_birthday"
        ),
        InlineKeyboardButton(
            text="Другое",
            callback_data=f"add-event_other"
        )
    )

    keyboard.row(InlineKeyboardButton(
            text="<<Назад",
            callback_data="admin_back"
        )
    )
    return keyboard


def all_users_keyboard_for_event_creating(users: List[tables.User]):
    """Клавиатура всех пользователей для создания события"""
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{user.user_name} {datetime.strftime(user.birthday_date, '%d.%m.%Y')} ",
                callback_data=f"user-event_{user.id}"),
        )
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_add-event"
        )
    )
    return keyboard


def all_users_keyboard_for_except_from_event(users: List[tables.User]):
    """Клавиатура для исключения пользователя из события"""
    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{user.user_name} {datetime.strftime(user.birthday_date, '%d.%m.%Y')} ",
                callback_data=f"user-event-except_{user.id}"),
        )
    keyboard.adjust(2)
    keyboard.row(
        InlineKeyboardButton(
            text="Учесть всех", callback_data="user-event-except_all"
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text="Отмена", callback_data="something_cancel"
        )
    )
    return keyboard


def admin_pay_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text=f"{PAID1}", callback_data=f"paid_{PAID1}"),
        InlineKeyboardButton(text=f"{PAID2}", callback_data=f"paid_{PAID2}"),
        InlineKeyboardButton(text=f"{PAID3}", callback_data=f"paid_{PAID3}"),
    )

    keyboard.row(InlineKeyboardButton(
        text="Отмена", callback_data="something_cancel")
    )
    return keyboard


def all_events_keyboard_to_delete(events: List[tables.Event]):
    """Клавиатура администратора со всеми событиями"""
    keyboard = InlineKeyboardBuilder()

    for event in events:
        if event.title == "birthday":
            event_user = db.get_user_by_id(event.user_id)
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}",
                    callback_data=f"event_{event.id}"),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event.title}",
                    callback_data=f"event_{event.id}"),
            )
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="something_cancel"
        )
    )
    return keyboard


def all_events_to_ping_keyboard(events: List[tables.Event]):
    """Клавиатура администратора со всеми событиями для оповещения"""
    keyboard = InlineKeyboardBuilder()

    for event in events:
        if event.title == "birthday":
            event_user = db.get_user_by_id(event.user_id)
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}",
                    callback_data=f"ping_{event.id}"),
            )
        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"{datetime.strftime(event.event_date, '%d.%m.%Y')} {event.title}",
                    callback_data=f"ping_{event.id}"),
            )
    keyboard.adjust(2)

    keyboard.row(
        InlineKeyboardButton(
            text="Обо всех", callback_data="ping_all"
        )
    )

    keyboard.row(
        InlineKeyboardButton(
            text="<<Назад", callback_data="admin_back"
        )
    )
    return keyboard


def phone_choose_keyboard():
    """Клавиатура для создания телефона оплаты в событии"""
    phones = config.PHONES

    keyboard = InlineKeyboardBuilder()
    for phone in phones:
        keyboard.row(
            InlineKeyboardButton(
                text=phone, callback_data=f"phone_{phone}"
            )
        )

    keyboard.row(InlineKeyboardButton(text="Отмена", callback_data="something_cancel"))

    return keyboard
