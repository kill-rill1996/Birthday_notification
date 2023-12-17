import asyncio
from loguru import logger

from database.database import create_db
from services.bot_telegram import init_bot


if __name__ == "__main__":
    logger.info("Starting app")
    create_db()
    asyncio.run(init_bot())