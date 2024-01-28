from datetime import datetime

from aiogram import types


def hello_message(message: types.Message):
    """Приветственное сообщение"""
    return f"Hello, {message.from_user.full_name}!"


def successful_user_create_message(data: dict):
    """Сообщение об успешном создании пользователя"""
    return f"Пользователь <b>{data['user_name']} ({datetime.strftime(data['birthday_date'], '%d.%m.%Y')} г.)</b> зарегистрирован!"