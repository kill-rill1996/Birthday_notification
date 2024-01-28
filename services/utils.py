from datetime import date, datetime


def parse_birthday_date(message: str):
    return datetime.strptime(message, "%d.%m.%Y").date()

