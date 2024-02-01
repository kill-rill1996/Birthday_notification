import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import TOKEN
from database.database import create_db
from services.utils import set_commands
from services.middlewares import CheckRegistrationMiddleware
from services.routers import notifications, registration
from services.fsm_states import storage


async def init_bot() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher(storage=storage)
    await set_commands(bot)

    # middleware
    dp.message.middleware.register(CheckRegistrationMiddleware())
    # add routers
    dp.include_routers(registration.router, notifications.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting app")
    create_db()
    asyncio.run(init_bot())