from datetime import datetime
from typing import Union

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

import config
from services.middlewares import CheckIsAdminMiddleware
from services import keyboards as kb
from database import services as db
from services.messages import all_users_admin_message


router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(config.ADMINS))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'back')  # для возвращения с кнопки "назад"
@router.message(Command("admin"))   # для запуска с команды /admin
async def admin_panel_handler(message: Union[types.Message, types.CallbackQuery]):
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


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'delete-user')
async def delete_users_panel(callback: types.CallbackQuery):
    all_users = db.get_all_users()
    await callback.message.answer("Список всех пользователей:", reply_markup=kb.all_users_keyboard(all_users).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user')
async def delete_user(callback: types.CallbackQuery):
    """Удаление пользователя через панель администратора"""
    user_for_delete = db.get_user_by_id(int(callback.data.split('_')[1]))
    msg = f"Вы действительно хотите удалить пользователя <b>{user_for_delete.user_name} {datetime.strftime(user_for_delete.birthday_date, '%d.%m.%Y')}</b>"
    await callback.message.answer(msg, reply_markup=kb.yes_no_admin_keyboard(user_for_delete.id).as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split('_')[0] in ['yes', 'no'])
async def confirm_delete_user(callback: types.CallbackQuery):
    """Подтверждение удаления пользователя от администратора"""
    if callback.data.split("_")[0] == "yes":
        deleted_user = db.delete_user_by_id(int(callback.data.split('_')[1]))
        await callback.message.answer(f'Пользователь <b>"{deleted_user.user_name}"</b> удален', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer("Отмена удаления")
    await callback.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'users')
async def all_users(callback: types.CallbackQuery):
    """Список всех пользователей"""
    users = db.get_all_users()
    msg = all_users_admin_message(users)
    await callback.message.answer(msg, reply_markup=kb.back_admin_keyboard().as_markup(), parse_mode=ParseMode.HTML)
