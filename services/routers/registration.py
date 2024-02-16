from aiogram import Router
from datetime import datetime

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from services.fsm_states import FSMUserState
from services.messages import hello_message, successful_user_create_message, help_message
from services.utils import parse_birthday_date
from services import keyboards as kb
from services.errors import DateValidationError
import database.services as db


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(hello_message(message), parse_mode=ParseMode.HTML, reply_markup=kb.create_user_key_board().as_markup())
    await message.answer("Если у вас уже есть аккаунт - проигнорируйте это сообщение")


@router.message(Command("help"))
async def command_help_handler(message: types.Message):
    """Вспомогательная инструкция с помощью команды '/help'"""
    await message.answer(help_message())


# создание пользователя через команду (/registration)
@router.message(Command("registration"))
async def command_register_handler(message: types.Message, state: FSMContext):
    """Регистрация пользователя с помощью команды '/registration'"""

    # проверяем зарегистрирован ли пользователь
    user = db.get_user_by_tg_id(message.from_user.id)
    if user:
        await message.answer(f"Вы уже зарегистрированы. Ваши данные <b>{user.user_name} "
                             f"{datetime.strftime(user.birthday_date, '%d.%m.%Y')}</b>\n"
                             f"Вы можете изменить свой профиль с помощью команды /update "
                             f"или удалить его с помощью команды /delete", parse_mode=ParseMode.HTML)
    else:
        await state.set_state(FSMUserState.user_name)
        await message.answer("Укажите ваше имя", reply_markup=kb.cancel_inline_keyboard().as_markup())


# создание пользователя через кнопку (callback)
@router.callback_query(lambda callback: callback.data == "create_account", StateFilter(None))
async def create_user_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало создание пользователя, инициализация FSM"""
    # проверяем зарегистрирован ли пользователь
    user = db.get_user_by_tg_id(callback.from_user.id)
    if user:
        await callback.message.delete()
        await callback.message.answer(f"Вы уже зарегистрированы. Ваши данные <b>{user.user_name} "
                             f"{datetime.strftime(user.birthday_date, '%d.%m.%Y')}</b>\n"
                             f"Вы можете изменить свой профиль с помощью команды /update "
                             f"или удалить его с помощью команды /delete", parse_mode=ParseMode.HTML)
    else:
        await state.set_state(FSMUserState.user_name)
        await callback.message.answer("Укажите ваше имя", reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.message(FSMUserState.user_name)
async def add_username_fsm_handler(message: types.Message, state: FSMContext):
    """Добавление username в FSM"""
    await state.update_data(user_name=message.text)
    await state.set_state(FSMUserState.birthday_date)
    await message.answer("Отлично! Теперь введите дату рождения в формате <b>ДД.ММ.ГГГГ</b>",
                         reply_markup=kb.cancel_inline_keyboard().as_markup(),
                         parse_mode=ParseMode.HTML)


@router.message(FSMUserState.birthday_date)
async def add_birthday_date_handler(message: types.Message, state: FSMContext):
    """Добавление birthday date в FSM"""
    try:
        birthday_date_parsed = parse_birthday_date(message.text)
        await state.update_data(birthday_date=birthday_date_parsed)
        data = await state.get_data()

        # Создание пользователя в базе данных
        if message.from_user.username == None: # защита от пустого data["event_from_user"].username
            db.create_user(data, message.from_user.id, "")
        else:
            db.create_user(data, message.from_user.id, message.from_user.username)

        await message.answer(successful_user_create_message(data), parse_mode=ParseMode.HTML)
        await state.clear()

    except DateValidationError:
        await message.answer(f"Неверный формат даты. Попробуйте еще раз")


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'cancel', StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено")
    await callback.message.delete()
