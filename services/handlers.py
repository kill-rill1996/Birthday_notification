from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters import StateFilter

from services.fsm_states import storage, FSMUserState
from services.messages import hello_message, successful_user_create_message
from services.utils import parse_birthday_date
from services.keyboards import create_user_key_board, cancel_inline_keyboard
from config import SALT as s
from services.errors import DateValidationError
import database.services as db

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(hello_message(message), parse_mode=ParseMode.HTML)
    await message.answer("Создайте аккаунт", reply_markup=create_user_key_board().as_markup())


async def create_user_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало создание пользователя, инициализация FSM"""
    await state.set_state(FSMUserState.user_name)
    await callback.message.answer("Укажите ваше имя", reply_markup=cancel_inline_keyboard().as_markup())


async def add_username_fsm_handler(message: types.Message, state: FSMContext):
    """Добавление username в FSM"""
    await state.update_data(user_name=message.text)
    await state.set_state(FSMUserState.birthday_date)
    await message.answer("Отлично! Теперь введите дату рождения в формате <b>ДД.ММ.ГГГГ</b>",
                         reply_markup=cancel_inline_keyboard().as_markup(),
                         parse_mode=ParseMode.HTML)


async def add_birthday_date_handler(message: types.Message, state: FSMContext):
    """Добавление birthday date в FSM"""
    try:
        birthday_date_parsed = parse_birthday_date(message.text)
        await state.update_data(birthday_date=birthday_date_parsed)
        data = await state.get_data()

        # Создание пользователя в базе данных
        db.create_user(data, message.from_user.id)

        await message.answer(successful_user_create_message(data), parse_mode=ParseMode.HTML)
        await state.clear()

    except DateValidationError:
        await message.answer(f"Неверный формат даты. Попробуйте еще раз")


async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Создайте аккаунт", reply_markup=create_user_key_board().as_markup())


def dp_register_handlers(dp: Dispatcher):
    """register all handlers"""
    # create new user
    dp.callback_query.register(create_user_handler, lambda callback: callback.data == "Создать аккаунт", StateFilter(None))
    dp.message.register(add_username_fsm_handler, FSMUserState.user_name)
    dp.message.register(add_birthday_date_handler, FSMUserState.birthday_date)

    dp.callback_query.register(cancel_handler, lambda callback: callback.data == 'cancel', StateFilter("*"))






