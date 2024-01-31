from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers import dp, dp_register_handlers


from config import TOKEN
from .utils import set_commands


async def init_bot() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await set_commands(bot)
    dp_register_handlers(dp)

    await dp.start_polling(bot)



