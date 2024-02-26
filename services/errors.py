
class DateValidationError(Exception):
    pass


class DatePeriodError(Exception):
    pass


class WrongDateError(Exception):
    """Ошибка если дата меньше сегодняшей даты"""
    pass

