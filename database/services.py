from database import tables
from .database import Session


def create_user(data: dict, tg_id: int):
    with Session() as session:
        user = tables.User(user_name=data["user_name"], telegram_id=tg_id, birthday_date=data["birthday_date"])
        session.add(user)
        session.commit()

