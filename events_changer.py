from datetime import datetime, timedelta

from database import services as db
from database import database


def main():
    # поверяем актуальность существующих событий и удаляем прошедшие

    # добавляем новые события и плательщиков в table Payers
    users = db.get_all_users()
    for user in users:
        if is_less_then_30_days(user.birthday_date):
            # create new event
            db.create_event_and_payers(user.id)
            print("Создано новое событие")

    # рассылаем напоминания о текущих событиях если необходимо
    pass


def is_less_then_30_days(birth_date: datetime) -> bool:
    today_date = datetime.now().date()
    # составляем дату дня рождения в текущем году
    birthday_date_in_this_year = datetime.strptime(f"{birth_date.day}.{birth_date.month}.{today_date.year}",
                                                   "%d.%m.%Y").date()
    # проверяем ближе она чем 30 дней или нет
    if birthday_date_in_this_year > today_date and birthday_date_in_this_year < today_date + timedelta(days=30):
        return True

    return False


if __name__ == "__main__":
    main()