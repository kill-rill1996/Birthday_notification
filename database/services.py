import datetime
from typing import List

from database import tables
from .database import Session


def create_user(data: dict, tg_id: int):
    with Session() as session:
        user = tables.User(user_name=data["user_name"], telegram_id=tg_id, birthday_date=data["birthday_date"])
        session.add(user)
        session.commit()


def get_events_for_month(tg_id: int) -> List[tables.Event]:
    with Session() as session:
        user = get_user_by_tg_id(tg_id)
        events = session.query(tables.Event).filter(tables.Event.user_id != user.id).all()
        return events


def get_all_events() -> List[tables.Event]:
    with Session() as session:
        events = session.query(tables.Event).all()
        return events


def create_event_and_payers(user_id: int) -> tables.Event:
    with Session() as session:
        # создаем событие
        event = tables.Event(active=True, user_id=user_id)
        session.add(event)
        session.commit()

        # создаем плательщиков
        users = session.query(tables.User).filter(tables.User.id != user_id).all()
        for user in users:
            payer = tables.Payer(payment_status=False, summ=0, user_id=user.id, event_id=event.id)
            session.add(payer)
            session.commit()
        return event


def get_all_users() -> List[tables.User]:
    with Session() as session:
        users = session.query(tables.User).all()
        return users


def get_user_by_tg_id(tg_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        return user


def delete_user(tg_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        session.delete(user)
        session.commit()
        return user


def update_user_username(tg_id: int, username: str):
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        user.user_name = username
        session.commit()


def update_user_birthdate(tg_id: int, birthday_date: datetime.date):
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        user.birthday_date = birthday_date
        session.commit()
