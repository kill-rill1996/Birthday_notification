from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from database import services as db


def main():
    # поверяем актуальность существующих событий и удаляем прошедшие
    events = db.get_all_events()
    for event in events:
        if event.event_date < datetime.now().date():
            print(f"удаляем событие пользователя {event.user_id}")
            db.delete_event(event.id)

    # добавляем новые события и плательщиков в table Payers
    users = db.get_all_users()
    for user in users:
        if is_less_then_31_days(user.birthday_date):
            # create new event and payers
            # обработка ошибки по дубликатам
            try:
                db.create_event_and_payers(user.id, user.birthday_date)
                print("Создано новое событие")
            except IntegrityError:
                print("Событие уже есть в базе данных")

    # рассылаем напоминания о текущих событиях если необходимо
    update_events = db.get_all_events()
    for event in update_events:
        days_before = check_days_count_before_event(event.event_date)
        if days_before:
            pass
        elif days_before == 10:
            pass
        elif days_before == 5:
            pass
        elif days_before == 1:
            pass
        elif days_before == 0:
            pass


def check_days_count_before_event(event_date: datetime) -> datetime.date:
    date_now = datetime.now().date()
    days_before_event = event_date - date_now
    return days_before_event.days


def is_less_then_31_days(birth_date: datetime) -> bool:
    today_date = datetime.now().date()
    # составляем дату дня рождения в текущем году
    birthday_date_in_this_year = transform_birthdate_in_current_year(birth_date) # TODO cделать проверку для перехода на след год
    # проверяем ближе она чем 30 дней или нет
    if birthday_date_in_this_year > today_date and birthday_date_in_this_year < today_date + timedelta(days=31):
        return True

    return False


def transform_birthdate_in_current_year(birth_date: datetime) -> datetime.date:
    return datetime.strptime(f"{birth_date.day}.{birth_date.month}.{datetime.now().date().year}", "%d.%m.%Y").date()


if __name__ == "__main__":
    main()