from datetime import datetime
from typing import List

from aiogram import types

from database import tables


def hello_message(message: types.Message):
    """Приветственное сообщение todo - посмотреть бота ботаним"""
    return f"Привет! Можете зарегистрироваться с помощью команды /registration"


def successful_user_create_message(data: dict):
    """Сообщение об успешном создании пользователя"""
    return f"Пользователь <b>{data['user_name']} ({datetime.strftime(data['birthday_date'], '%d.%m.%Y')} г.)</b> зарегистрирован!"


def upcoming_events_message(events: List[tables.Event]) -> str:
    """Сообщение о ближайщих событиях"""
    if events:
        msg = "В ближайщий месяц будут следующие события:\n"
        for idx, event in enumerate(events):
            sub_msg = f"{idx + 1}. <b>{datetime.strftime(event.user.birthday_date, '%d.%m.%Y')}</b> день рождения у пользователя <b>{event.user.user_name}</b>\n"
            msg += sub_msg
        msg.rstrip()
    else:
        msg = "В ближайщий месяц событий нет"
    return msg


def profile_message(username: str, birthday_date: datetime.date) -> str:
    parsed_birthday_date = datetime.strftime(birthday_date, '%d.%m.%Y')
    msg = f"Ваши данные\nИмя <b>'{username}'</b> дата рождения <b>'{parsed_birthday_date}'</b>\n\n" \
          f"Вы можете изменить профиль с помощью команды /update или удалить с помощью команды /delete"
    return msg

