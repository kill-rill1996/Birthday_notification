from typing import List

from sqlalchemy.orm import joinedload

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
        for event in events:
            print(event)
        return events


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


def update_user_username():
    pass


def update_user_birthdate():
    pass