from datetime import datetime

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from services.errors import DateValidationError, DatePeriodError, PhoneNumberError


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


def validate_phone_number(phone_number: str) -> None:
    """Проверка валидности номера телефона"""
    if len(phone_number) != 11:
        raise PhoneNumberError

    for char in phone_number:
        if char.isalpha():
            raise PhoneNumberError


def parse_phone_number(phone: str) -> str:
    """Изменение формата номера телефона"""
    new_phone = f"{phone[0]}-({phone[1]}{phone[2]}{phone[3]})-{phone[4]}{phone[5]}{phone[6]}-{phone[7]}{phone[8]}" \
                f"-{phone[9]}{phone[10]}"

    return new_phone


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

