import datetime
from typing import List
from sqlalchemy.orm import joinedload

from database import tables
from .database import Session
from events_changer import transform_birthdate_in_current_year


def create_user(data: dict, tg_id: int, tg_username: str) -> None:
    """Создание пользователя и его payers на все существующие события"""
    with Session() as session:
        user = tables.User(user_name=data["user_name"],
                           telegram_id=tg_id,
                           birthday_date=data["birthday_date"],
                           tg_username=tg_username)
        session.add(user)
        session.commit()

        # добавление payer на ближайшие события, если пользователь зарегистрировался позже
        events = session.query(tables.Event).all()
        if events:
            for event in events:
                payer = tables.Payer(payment_status=False, summ=0, user_id=user.id, event_id=event.id)
                session.add(payer)
                session.commit()

        # TODO надо ли создавать события если человек зарегистрировался за пару дней??


def get_events_for_month(tg_id: int) -> (List[tables.Event], List[tables.User], int):
    """Получение событий на ближайший месяц с payers,
    users, которые должны оплатить событие, и user id у которого событие"""
    with Session() as session:
        user = get_user_by_tg_id(tg_id)
        events_with_payers = session.query(tables.Event).filter(tables.Event.user_id != user.id)\
            .options(joinedload(tables.Event.payers)).all()

        event_users = []
        for event in events_with_payers:
            event_users.append(get_user_by_id(event.user_id)) #TODO добавить не ДР
        return events_with_payers, event_users, user.id


def get_all_events() -> List[tables.Event]:
    """Получение всех событий"""
    with Session() as session:
        events = session.query(tables.Event).options(joinedload(tables.Event.payers))\
            .order_by(tables.Event.event_date).all()
        return events


def get_all_events_birthday() -> List[tables.Event]:
    """Получение всех событий с title birthday"""
    with Session() as session:
        events = session.query(tables.Event).filter(tables.Event.title == "birthday").options(joinedload(tables.Event.payers))\
            .order_by(tables.Event.event_date).all()
        return events


def create_event_and_payers(user_id: int | None, birthday_date: datetime, title: str = "birthday") -> tables.Event:
    """Создание event и payers для этого ивента"""
    with Session() as session:
        # создаем событие
        if title == "birthday":
            event_date = transform_birthdate_in_current_year(birthday_date)
        else:
            event_date = birthday_date
        event = tables.Event(active=True, user_id=user_id, event_date=event_date, title=title)
        session.add(event)
        session.commit()

        # создаем плательщиков
        if user_id:
            # пользователи за исключением именинника
            users = session.query(tables.User).filter(tables.User.id != user_id).all()
        else:
            # все пользователи если именинник не указан
            users = session.query(tables.User).all()

        for user in users:
            payer = tables.Payer(payment_status=False, summ=0, user_id=user.id, event_id=event.id)
            session.add(payer)
            session.commit()

        return event


def get_all_users() -> List[tables.User]:
    """Получение всех пользователей"""
    with Session() as session:
        users = session.query(tables.User).all()
        return users


def get_user_by_id(user_id: int) -> tables.User:
    """Получению пользователя по user id"""
    with Session() as session:
        user = session.query(tables.User).filter(tables.User.id == user_id).first()
        return user


def delete_event(event_id: int) -> tables.Event:
    """Удаление события с помощью event id"""
    with Session() as session:
        event = session.query(tables.Event).filter_by(id=event_id).first()
        session.delete(event)
        session.commit()
        return event


def get_user_by_tg_id(tg_id: int) -> tables.User:
    """Получение пользователя с помощью telegram_id"""
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        return user


def delete_user_by_tg_id(tg_id: int) -> tables.User:
    """Удаление пользователя с помощью telegram_id"""
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        session.delete(user)
        session.commit()
        return user


def delete_user_by_id(user_id: int) -> tables.User:
    """Удаление пользователя с помощью id"""
    with Session() as session:
        user = session.query(tables.User).filter_by(id=user_id).first()
        session.delete(user)
        session.commit()
        return user


def update_user_username(tg_id: int, username: str) -> None:
    """Изменение имени пользователя"""
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        user.user_name = username
        session.commit()


def update_user_birthdate(tg_id: int, birthday_date: datetime.date) -> None:
    """Изменение дня рождения"""
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        user.birthday_date = birthday_date
        session.commit()


def get_event_and_user_by_event_id(event_id: int) -> (tables.Event, List[tables.User], List[tables.User]):
    """Получение event, пользователя у которого событие и список user, которые должны оплатить через payer id"""
    with Session() as session:
        event = session.query(tables.Event).options(joinedload(tables.Event.payers)).filter_by(id=event_id).first()

        event_user = get_user_by_id(event.user_id)

        payer_users = []
        for payer in event.payers:
            user = get_user_by_id(payer.user_id)
            payer_users.append(user)

        return event, event_user, payer_users


def get_user_by_payer_id(payer_id: int) -> tables.User:
    """Получение user через payer id"""
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        user = get_user_by_id(payer.user_id)

        return user


def add_payment(payer_id: int, amount: int) -> None:
    """Добавление оплаты в payer и суммы оплат в event"""
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        payer.summ = amount
        payer.payment_status = True

        event = session.query(tables.Event).filter_by(id=payer.event_id).first()
        event.summ += amount
        session.commit()


def get_event_from_payer_id(payer_id: int) -> tables.Event:
    """Получение event через payer id"""
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        event = session.query(tables.Event).filter_by(id=payer.event_id).first()
        return event


def get_event_by_event_id(event_id: int) -> tables.Event:
    """Получение event через event_id"""
    with Session() as session:
        event = session.query(tables.Event).filter_by(id=event_id).first()
        return event
