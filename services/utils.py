from datetime import date, datetime

from services.errors import DateValidationError


def parse_birthday_date(message: str):
    try:
        result = datetime.strptime(message, "%d.%m.%Y").date()
        if result.year > datetime.now().year:
            raise DateValidationError
    except Exception:
        raise DateValidationError
    return result

