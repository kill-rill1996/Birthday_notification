import datetime
from typing import List
from sqlalchemy.orm import joinedload

from database import tables
from .database import Session
from events_changer import transform_birthdate_in_current_year


def create_user(data: dict, tg_id: int, tg_username: str):
    with Session() as session:
        user = tables.User(user_name=data["user_name"],
                           telegram_id=tg_id,
                           birthday_date=data["birthday_date"],
                           tg_username=tg_username)
        session.add(user)
        session.commit()

        # добавление payer на ближайшие события, если пользователь зарегистрировался позже
        # TODO надо ли создавать события если человек зарегистрировался за пару дней??
        events = session.query(tables.Event).all()
        if events:
            for event in events:
                payer = tables.Payer(payment_status=False, summ=0, user_id=user.id, event_id=event.id)
                session.add(payer)
                session.commit()


def get_events_for_month(tg_id: int) -> (List[tables.Event], List[tables.User], int):
    with Session() as session:
        user = get_user_by_tg_id(tg_id)
        events_with_payers = session.query(tables.Event).filter(tables.Event.user_id != user.id)\
            .options(joinedload(tables.Event.payers)).all()

        event_users = []
        for event in events_with_payers:
            event_users.append(get_user_by_id(event.user_id))
        return events_with_payers, event_users, user.id


def get_all_events() -> List[tables.Event]:
    with Session() as session:
        events = session.query(tables.Event).options(joinedload(tables.Event.payers))\
            .order_by(tables.Event.event_date).all()
        return events


def create_event_and_payers(user_id: int, birthday_date: datetime) -> tables.Event:
    with Session() as session:
        # создаем событие
        event_date = transform_birthdate_in_current_year(birthday_date)
        event = tables.Event(active=True, user_id=user_id, event_date=event_date)
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


def get_user_by_id(user_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter(tables.User.id == user_id).first()
        return user


def delete_event(event_id: int) -> tables.Event:
    with Session() as session:
        event = session.query(tables.Event).filter_by(id=event_id).first()
        session.delete(event)
        session.commit()
        return event


def get_user_by_tg_id(tg_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        return user


def delete_user_by_tg_id(tg_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter_by(telegram_id=tg_id).first()
        session.delete(user)
        session.commit()
        return user


def delete_user_by_id(user_id: int) -> tables.User:
    with Session() as session:
        user = session.query(tables.User).filter_by(id=user_id).first()
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


def get_event_and_user_by_event_id(event_id: int):
    with Session() as session:
        event = session.query(tables.Event).options(joinedload(tables.Event.payers)).filter_by(id=event_id).first()

        event_user = get_user_by_id(event.user_id)

        payer_users = []
        for payer in event.payers:
            user = get_user_by_id(payer.user_id)
            payer_users.append(user)

        return event, event_user, payer_users


def get_user_by_payer_id(payer_id: int):
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        user = get_user_by_id(payer.user_id)

        return user


def add_payment(payer_id: int, amount: int):
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        payer.summ = amount
        payer.payment_status = True

        event = session.query(tables.Event).filter_by(id=payer.event_id).first()
        event.summ += amount
        session.commit()


def get_event_from_payer_id(payer_id: int):
    with Session() as session:
        payer = session.query(tables.Payer).filter_by(id=payer_id).first()
        event = session.query(tables.Event).filter_by(id=payer.event_id).first()
        return event