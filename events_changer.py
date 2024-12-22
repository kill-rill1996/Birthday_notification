from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from database import services as db


def main():
    """Работает по crone раз в день"""
    # поверяем актуальность существующих событий и удаляем прошедшие
    events = db.get_all_events(only_active=False)
    for event in events:
        if event.event_date < datetime.now().date():
            print(f"удаляем событие пользователя {event.user_id} {datetime.strftime(datetime.now(), '%d.%m.%Y')}")
            db.delete_event(event.id)

    # добавляем новые события и плательщиков в table Payers
    users = db.get_all_users()
    events_birthday = db.get_all_events_birthday(only_active=True)
    user_ids_with_birthday = [event.user_id for event in events_birthday]
    for user in users:
        # проверяем есть ли уже активное событие этого пользователя с тэгом birthday
        if events:
            if user.id not in user_ids_with_birthday and is_less_then_31_days(user.birthday_date):
                db.create_event_and_payers(user.id, user.birthday_date)
                print("Создано новое событие " + datetime.strftime(datetime.now(), '%d.%m.%Y'))
        else:
            if is_less_then_31_days(user.birthday_date):
                db.create_event_and_payers(user.id, user.birthday_date)
                print("Создано новое событие" + datetime.strftime(datetime.now(), '%d.%m.%Y'))


def check_days_count_before_event(event_date: datetime) -> datetime.date:
    date_now = datetime.now().date()
    days_before_event = event_date - date_now
    return days_before_event.days


def is_less_then_31_days(birth_date: datetime) -> bool:
    today_date = datetime.now().date()

    # составляем дату дня рождения в текущем году
    birthday_date_in_this_year = transform_birthdate_in_current_year(birth_date)

    # проверяем ближе она чем 30 дней или нет
    if birthday_date_in_this_year > today_date and birthday_date_in_this_year < today_date + timedelta(days=31):
        return True

    # проверяем др в январе след. года
    elif birthday_date_in_this_year.month == 1 and today_date.month == 12:
        if birthday_date_in_this_year + timedelta(days=365) < today_date + timedelta(days=31):
            return True

    return False


def transform_birthdate_in_current_year(birth_date: datetime) -> datetime.date:
    # date_current_year = datetime.strptime(f"{birth_date.day}.{birth_date.month}.{datetime.now().date().year}", "%d.%m.%Y").date()

    # 2023-01-17
    # 17.01.2024
    # если др в январе, но создано событие будет в декабре, меняем год на +1
    if datetime.now().month == 12 and birth_date.month == 1:
        return datetime.strptime(f"{birth_date.day}.{birth_date.month}.{datetime.now().date().year + 1}", "%d.%m.%Y").date()

    # if birth_date.month == 12:
    #     date_current_year += timedelta(days=31)

    return datetime.strptime(f"{birth_date.day}.{birth_date.month}.{datetime.now().date().year}", "%d.%m.%Y").date()


if __name__ == "__main__":
    main()