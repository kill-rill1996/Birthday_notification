import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from config import TOKEN
from database.database import create_db
from database.services import get_all_users_without_admin, get_all_events, get_event_by_event_id
from services.messages import ping_user
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
        users = get_all_users_without_admin(callback.from_user.id)

        if callback.data.split("_")[1] == "all":
            events_with_payers = get_all_events()
            for user in users:
                msg = ping_user(user, events_with_payers)
                await bot.send_message(user.telegram_id, msg)
        else:
            event_id = int(callback.data.split("_")[1])
            # event_with_payers = get_event_by_event_id(event_id)
            for user in users:
                await bot.send_message(user.telegram_id, f"hello")

        await callback.message.answer("Пользователи оповещены")

    # add routers
    dp.include_routers(administration.router, registration.router, notifications.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting app")
    create_db()
    asyncio.run(init_bot())