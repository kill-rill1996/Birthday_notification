import asyncio
from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import TelegramObject

from database.services import get_user_by_tg_id


class CheckRegistrationMiddleware(BaseMiddleware):
    """Проверка зарегистрирован пользователь или нет"""

    def is_registered_user(self, tg_id: int) -> bool:
        user = get_user_by_tg_id(tg_id)
        if user:
            return True
        return False

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # проверка функции на доступность для незарегистрированных пользователей
        is_open_operation = get_flag(data, "not_private_operation")
        if is_open_operation:
            return await handler(event, data)

        # проверка зарегистрирован ли пользователь
        if self.is_registered_user(data["event_from_user"].id):
            return await handler(event, data)

        # ответ для незарегистрированных пользователей
        await event.answer(
            "Для использования бота, вам необходимо зарегистрироваться!\n\n"
            "Вы можете зарегистрироваться с помощью команды /registration",
            show_alert=True
        )
        return

