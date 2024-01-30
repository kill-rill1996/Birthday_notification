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
            sub_msg = f"{idx + 1}. <b>{event.user.birthday_date}</b> день рождения у пользователя <b>{event.user.user_name}</b>\n"
            msg += sub_msg
        msg.rstrip()
    else:
        msg = "В ближайщий месяц событий нет"
    return msg

