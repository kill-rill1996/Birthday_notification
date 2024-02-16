from typing import Union

from aiogram import Router, types
from aiogram.filters import Command

import config
from services.middlewares import CheckIsAdminMiddleware
from services import keyboards as kb
from database import services as db


router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(config.ADMINS))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'back')  # для возвращения с кнопки "назад"
@router.message(Command("admin"))   # для запуска с команды /admin
async def command_help_handler(message: Union[types.Message, types.CallbackQuery]):
    """Панель inline кнопок для администратора"""
    if type(message) == types.Message:
        await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
    else:
        await message.message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
        await message.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'events')
async def events_handler(callback: types.CallbackQuery):
    events = db.get_all_events()
    await callback.message.answer("Список всех активных событий:", reply_markup=kb.all_events_keyboard(events).as_markup())


