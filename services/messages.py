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
            sub_msg = f"{idx + 1}. <b>{datetime.strftime(event.event_date, '%d.%m.%Y')}</b> день рождения у пользователя <b>{event.user.user_name}</b>\n"
            msg += sub_msg
        msg.rstrip()
    else:
        msg = "В ближайщий месяц событий нет"
    return msg


def profile_message(username: str, birthday_date: datetime.date) -> str:
    parsed_birthday_date = datetime.strftime(birthday_date, '%d.%m.%Y')
    msg = f"Ваши данные\nИмя <b>{username}</b> дата рождения <b>{parsed_birthday_date}</b>\n\n" \
          f"Вы можете изменить профиль с помощью команды /update или удалить с помощью команды /delete"
    return msg


def all_users_admin_message(users: List[tables.User]):
    message = "Список зарегистрированных пользователей:\n\n"
    for count, user in enumerate(users, start=1):
        if user.tg_username == "":
            message += f"{count}. <b>{user.user_name}</b> {datetime.strftime(user.birthday_date, '%d.%m.%Y')}\n"
        else:
            message += f"{count}. <b>{user.user_name}</b> {datetime.strftime(user.birthday_date, '%d.%m.%Y')} {'@' + user.tg_username}\n"
    return message


def help_message() -> str:
    msg = "Бот помогает вести учет событий и напоминать о них пользователям.\n\n" \
          "Использовать команды можно с помощью вкладки \"Меню\".\n\n" \
          "Команды бота:\n\n" \
          "/start — старт бота и приветственное сообщение\n" \
          "/registration — регистрация пользователя, если он еще не зарегистрирован\n" \
          "/events — события, которые произойдут в ближайщий месяц\n" \
          "/profile — просмотр ваших данных (имя пользователя и дата рождения, указанные при регистрации)\n" \
          "/update — изменение ваших данных\n" \
          "/delete — удаление пользователя\n" \
          "/help — справка\n" \
          "/admin — панель администратора"

    return msg


def admin_event_info_message(event: tables.Event, event_user: tables.User, payer_users: List[tables.User]) -> str:
    msg = f"<b>{datetime.strftime(event.event_date, '%d.%m.%Y')} {event_user.user_name}</b>\n" \
          f"Собранная сумма {event.summ} р.\n\n"
    for idx, payer in enumerate(event.payers, start=1):
        for user in payer_users:
            if payer.user_id == user.id:
                sub_msg = f"{idx}. {user.user_name}"
                if payer.payment_status:
                    sub_msg += " ✅ "
                else:
                    sub_msg += " ❌ "
                sub_msg += f"сумма {payer.summ} р.\n"
                msg += sub_msg

    return msg.rstrip()


