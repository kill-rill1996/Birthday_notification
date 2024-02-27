from datetime import datetime

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from services.errors import DateValidationError, DatePeriodError


def parse_birthday_date(message: str) -> datetime.date:
    """Проверяет валидность введенной даты и переводит в формат datetime"""
    try:
        result = datetime.strptime(message, "%d.%m.%Y").date()
        if result.year > datetime.now().year:
            raise DateValidationError
    except Exception:
        raise DateValidationError
    return result


def check_validation_date(message: str) -> datetime.date:
    """Проверяет валидность даты для добавляемых событий"""
    try:
        result = datetime.strptime(message, "%d.%m.%Y").date()
        if result.year < datetime.now().year or result.year > datetime.now().year + 1:
            raise DatePeriodError
    except ValueError:
        raise DateValidationError
    return result


async def set_commands(bot: Bot):
    """Устанавливает перечень команд для бота"""
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="registration", description="Регистрация"),
        BotCommand(command="events", description="Ближайшие события"),
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="update", description="Изменить профиль"),
        BotCommand(command="delete", description="Удалить профиль"),
        BotCommand(command="help", description="Справочная информация"),
        BotCommand(command="admin", description="Панель администратора"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())

