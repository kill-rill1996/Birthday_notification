import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode

from config import TOKEN

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def notify():
    tg_ids = [714371204, 420551454]
    for tg_id in tg_ids:
        await bot.send_message(tg_id, "test message")
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(notify())
