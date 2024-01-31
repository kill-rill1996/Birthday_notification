from datetime import date, datetime

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from services.errors import DateValidationError


def parse_birthday_date(message: str):
    try:
        result = datetime.strptime(message, "%d.%m.%Y").date()
        if result.year > datetime.now().year:
            raise DateValidationError
    except Exception:
        raise DateValidationError
    return result


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="registration", description="Регистрация"),
        BotCommand(command="events", description="Ближайшие события"),
        BotCommand(command="profile", description="Профиль"),
        BotCommand(command="update", description="Изменение профиля"),
        BotCommand(command="delete", description="Удаление профиля"),
        BotCommand(command="help", description="Справка"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())

