import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from config import TOKEN
from database.database import create_db
from database.services import get_all_users, get_all_events, get_event_users, get_event_by_event_id
from services.keyboards import admins_keyboard
from services.messages import ping_user_message
from services.utils import set_commands
from services.routers import notifications, registration, administration
from services.fsm_states import storage


async def init_bot() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher(storage=storage)
    await set_commands(bot)

    # handler для оповещения клиентов
    @administration.router.callback_query(lambda callback: callback.data.split("_")[0] == "ping")
    async def notify_users(callback: types.CallbackQuery):
        all_users = get_all_users()
        event_users = get_event_users()

        # отправка сообщений обо всех событиях
        if callback.data.split("_")[1] == "all":
            events_with_payers = get_all_events()
            for user_to_send in all_users:
                msg = ping_user_message(user_to_send, event_users, events_with_payers)
                if msg: # чтобы не оповещать пользователя о его др
                    await bot.send_message(user_to_send.telegram_id, msg)

        # отправка сообщений о конкретном событии
        else:
            event_id = int(callback.data.split("_")[1])
            event_with_payers = get_event_by_event_id(event_id)
            for user in all_users:
                msg = ping_user_message(user, event_users, event_with_payers)
                if msg:  # чтобы не оповещать пользователя о его событии
                    await bot.send_message(user.telegram_id, msg)

        # сообщение админу
        await callback.message.answer("Пользователи оповещены 📝")
        # сообщение с меню админа
        await callback.message.answer("Выберите действие", reply_markup=admins_keyboard().as_markup())

    # add routers
    dp.include_routers(administration.router, registration.router, notifications.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting app")
    create_db()
    asyncio.run(init_bot())