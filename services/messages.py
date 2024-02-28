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


def upcoming_events_message(events_with_payers: List[tables.Event], event_users: List[tables.User], user_id: int) -> str:
    """Сообщение о ближайщих событиях"""
    if events_with_payers:
        msg = "В ближайший месяц будут следующие события:\n\n"

        for idx, event in enumerate(events_with_payers, start=1):
            # проверка на тип события (др или другое)
            if event.title == "birthday": # др
                for user in event_users:
                    if event.user_id == user.id:
                        sub_msg = f"{idx}. <b>{datetime.strftime(event.event_date, '%d.%m.%Y')}</b> день рождения у пользователя <b>{user.user_name}</b>\n"
                        msg += sub_msg

            else: # другое
                sub_msg = f"{idx}. <b>{datetime.strftime(event.event_date, '%d.%m.%Y')}</b> <b>{event.title}</b>\n"
                msg += sub_msg

            # плательщики для события
            for payer in event.payers:
                if payer.user_id == user_id:
                    if payer.payment_status:
                        msg += f"✅ Событие оплачено ({payer.summ}р.)\n\n"
                    else:
                        msg += f"❌ Событие не оплачено\n\n"
        msg.rstrip()
    else:
        msg = "В ближайший месяц событий нет"
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
          "/events — события, которые произойдут в ближайший месяц\n" \
          "/profile — просмотр ваших данных (имя пользователя и дата рождения, указанные при регистрации)\n" \
          "/update — изменение ваших данных\n" \
          "/delete — удаление пользователя\n" \
          "/help — справка\n" \
          "/admin — панель администратора"

    return msg


def admin_event_info_message(event: tables.Event, event_user: tables.User, payer_users: List[tables.User]) -> str:
    if event.title == "birthday":

        msg = f"<b>{datetime.strftime(event.event_date, '%d.%m.%Y')} день рождения {event_user.user_name}</b>\n" \
              f"Собранная сумма <b>{event.summ} р.</b>\n\n"
    else:
        msg = f"<b>{datetime.strftime(event.event_date, '%d.%m.%Y')} {event.title}</b>\n" \
              f"Собранная сумма <b>{event.summ} р.</b>\n\n"

    already_payers_count = 0

    for idx, payer in enumerate(event.payers, start=1):
        for user in payer_users:
            if payer.user_id == user.id:
                sub_msg = f"{idx}. <b>{user.user_name}</b>"

                if user.tg_username:
                    sub_msg += f" @{user.tg_username}"

                if payer.payment_status:
                    sub_msg += " ✅ "
                else:
                    sub_msg += " ❌ "
                    already_payers_count += 1

                if payer.summ:
                    sub_msg += f"- <b>{payer.summ} р.</b>"

                msg += f"\n{sub_msg}"

    if already_payers_count:
        msg += "\n\nНиже указаны пользователи, которые не оплатили событие"
    else:
        msg += "\n\nДанное событие оплатили все пользователи"

    return msg.rstrip()


def admin_event_payer_info_message(user: tables.User) -> str:
    msg = f"Пользователь <b>{user.user_name}</b> еще не оплатил событие\n\n"

    return msg


def admin_successful_create_event_birthday(user: tables.User) -> str:
    """Сообщение об успешном создании администратором внепланового ДР"""
    msg = f'Событие "День рождения <b>{user.user_name}"</b> на <b>{datetime.strftime(user.birthday_date, "%d.%m.%Y")}</b> успешно создано!'
    return msg


def admin_event_delete_confirmation(event: tables.Event) -> str:
    """Сообщение о подтверждении удаления события"""
    msg = f'Вы действительно хотите удалить это событие <b>{event.title if event.title != "birthday" else "День рождения"} {datetime.strftime(event.event_date, "%d.%m.%Y")}</b>?'
    return msg


def ping_user_message(user_to_send: tables.User, event_users: List[tables.User], events_with_payers: List[tables.Event] | tables.Event) -> str:
    """Сообщение пользователям о ближайщих событиях"""

    # напоминание обо всех событиях
    if type(events_with_payers) == list: # обо всех событиях
        msg = "Напоминаем о ближайших событиях\n\n"
        counter = 1

        for idx, event in enumerate(events_with_payers, start=1):
            # проверка на тип события (др или другое)
            if event.title == "birthday":  # др
                for user in event_users:
                    if event.user_id == user.id and event.user_id != user_to_send.id:
                        sub_msg = f"{counter}. <b>{datetime.strftime(event.event_date, '%d.%m.%Y')}</b> день рождения у пользователя <b>{user.user_name}</b>\n"
                        msg += sub_msg
                        counter += 1

            else:  # другое
                sub_msg = f"{counter}. <b>{datetime.strftime(event.event_date, '%d.%m.%Y')}</b> <b>{event.title}</b>\n"
                msg += sub_msg
                counter += 1

            # плательщики для события
            for payer in event.payers:
                if payer.user_id == user_to_send.id and event.user_id != user_to_send.id:
                    if payer.payment_status:
                        msg += f"✅ Событие оплачено ({payer.summ}р.)\n\n"
                    else:
                        msg += f"❌ Событие не оплачено\n\n"
        msg.rstrip()
    else: # конкретное событие
        msg = "Напоминаем о приближающемся событии\n\n"
        len_message = len(msg)

        if events_with_payers.title == "birthday": # др
            for user in event_users:
                if events_with_payers.user_id == user.id and events_with_payers.user_id != user_to_send.id:
                    sub_msg = f"<b>{datetime.strftime(events_with_payers.event_date, '%d.%m.%Y')}</b> день рождения у пользователя <b>{user.user_name}</b>\n"
                    msg += sub_msg

        else: # другое
            sub_msg = f"<b>{datetime.strftime(events_with_payers.event_date, '%d.%m.%Y')}</b> <b>{events_with_payers.title}</b>\n"
            msg += sub_msg

        # плательщики для события
        for payer in events_with_payers.payers:
            if payer.user_id == user_to_send.id and events_with_payers.user_id != user_to_send.id:
                if payer.payment_status:
                    msg += f"✅ Событие оплачено ({payer.summ}р.)\n\n"
                else:
                    msg += f"❌ Событие не оплачено\n\n"

        # сообщение для пользователя у которого др
        if len(msg) == len_message:
            msg = "Для вас в ближайшее время нет событий"

    return msg

