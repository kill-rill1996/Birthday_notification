from aiogram import Router, types
from aiogram.filters import Command

import config
from services.middlewares import CheckIsAdminMiddleware

router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(config.ADMINS))


@router.message(Command("admin"))
async def command_help_handler(message: types.Message):
    """Вспомогательная инструкция с помощью команды '/help'"""
    await message.answer("Вы администратор")