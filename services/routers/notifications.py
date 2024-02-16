from aiogram import Router
from datetime import datetime
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from services.fsm_states import FsmUpdateUser
from services.messages import upcoming_events_message, profile_message
from services.middlewares import CheckRegistrationMiddleware
from services.utils import parse_birthday_date
from services import keyboards as kb
from services.errors import DateValidationError
import database.services as db


router = Router()
router.message.middleware.register(CheckRegistrationMiddleware())


@router.message(Command("events"))
async def command_events_handler(message: types.Message):
    """Вывод событий на ближайший месяц с помощью команды '/events'"""
    events = db.get_events_for_month(message.from_user.id)
    msg = upcoming_events_message(events)
    await message.answer(msg, parse_mode=ParseMode.HTML)


@router.message(Command("delete"))
async def command_delete_self_user_handler(message: types.Message):
    """Удаление своего пользователя из БД"""
    msg = "Вы действительно хотите удалить свой профиль?"
    await message.answer(msg, reply_markup=kb.yes_no_keyboard().as_markup())


@router.message(Command("profile"))
async def command_profile_handler(message: types.Message):
    """Вывод своего профиля (имя и дата рождения)"""
    user = db.get_user_by_tg_id(message.from_user.id)
    msg = profile_message(user.user_name, user.birthday_date)
    await message.answer(msg, parse_mode=ParseMode.HTML)


@router.message(Command("update"))
async def command_update_profile_handler(message: types.Message):
    """Изменение данных своего профиля"""
    msg = "Выберите что хотите изменить"
    await message.answer(msg, reply_markup=kb.update_profile_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'update')
async def update_profile_handler(callback: types.CallbackQuery, state: FSMContext):
    """Получение новых данных для имени или даты рождения"""
    user = db.get_user_by_tg_id(callback.from_user.id)
    if callback.data.split("_")[0] == "name":
        await state.set_state(FsmUpdateUser.new_username)
        msg = f'Текущие имя пользователя "{user.user_name}", отправьте новое имя пользователя.'
    else:
        await state.set_state(FsmUpdateUser.new_birthday_date)
        birthday_date = datetime.strftime(user.birthday_date, '%d.%m.%Y')
        msg = f'Ваша дата рождения "{birthday_date}", отправьте дату дня рождения в формате ДД.ММ.ГГГГ.'
    await callback.message.edit_text(msg, reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.message(StateFilter(FsmUpdateUser.new_username, FsmUpdateUser.new_birthday_date))
async def update_profile_confirmation_handler(message: types.Message, state: FSMContext):
    """Оповещение об успешном изменении данных имени или даты рождения"""
    current_state = await state.get_state()
    if current_state == FsmUpdateUser.new_username:
        db.update_user_username(message.from_user.id, message.text)
        await state.clear()
        await message.answer("Имя успешно изменено")
    else:
        try:
            birthday_date_parsed = parse_birthday_date(message.text)
            db.update_user_birthdate(message.from_user.id, birthday_date_parsed)
            await state.clear()
            await message.answer("Дата рождения успешно изменена")
        except DateValidationError:
            await message.answer(f"Неверный формат даты. Необходимо ввести дату в формате <b>ДД.ММ.ГГГГ</b>. "
                                 f"Попробуйте еще раз", parse_mode=ParseMode.HTML,
                                 reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'delete')
async def confirm_delete_handler(callback: types.CallbackQuery):
    """Подтверждение удаления профиля"""
    if callback.data.split("_")[0] == "yes":
        deleted_user = db.delete_user_by_tg_id(callback.from_user.id)
        await callback.message.answer(f'Ваш профиль "{deleted_user.user_name}" удален')
    else:
        await callback.message.answer("Отмена удаления")
    await callback.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'cancel', StateFilter("*"), flags={"not_private_operation": "true"})
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено")
    await callback.message.delete()

