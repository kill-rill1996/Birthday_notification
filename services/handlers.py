from datetime import datetime

from aiogram import Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters import StateFilter

from services.fsm_states import storage, FSMUserState, FsmUpdateUser
from services.messages import hello_message, successful_user_create_message, upcoming_events_message
from services.utils import parse_birthday_date
from services import keyboards as kb
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
    await message.answer(hello_message(message), parse_mode=ParseMode.HTML, reply_markup=kb.create_user_key_board().as_markup())
    await message.answer("Если у вас уже есть аккаунт - проигнорируйте это сообщение")


@dp.message(Command("registration"))
async def command_register_handler(message: types.Message, state: FSMContext):
    """Регистрация пользователя с помощью команды '/registration'"""
    user = db.get_user_by_tg_id(message.from_user.id)

    if user:
        await message.answer(f"Вы уже зарегистрированы. Ваши данные <b>{user.user_name} "
                             f"{datetime.strftime(user.birthday_date, '%d.%m.%Y')}</b>\n"
                             f"Вы можете изменить свой профиль с помощью команды /update "
                             f"или удалить его с помощью команды /delete", parse_mode=ParseMode.HTML)
    else:
        await state.set_state(FSMUserState.user_name)
        await message.answer("Укажите ваше имя", reply_markup=kb.cancel_inline_keyboard().as_markup())


@dp.message(Command("help"))
async def command_help_handler(message: types.Message):
    """Вспомогательная инструкция с помощью команды '/help'"""
    await message.answer("Что умеет этот бот")


@dp.message(Command("events"))
async def command_events_handler(message: types.Message):
    """Вывод событий на ближайший месяц с помощью команды '/events'"""
    events = db.get_events_for_month(message.from_user.id)
    msg = upcoming_events_message(events)
    await message.answer(msg, parse_mode=ParseMode.HTML)


@dp.message(Command("delete"))
async def command_delete_self_user_handler(message: types.Message):
    """Удаление своего пользователя из БД"""
    msg = "Вы действительно хотите удалить свой профиль?"
    await message.answer(msg, reply_markup=kb.yes_no_keyboard().as_markup())


@dp.message(Command("update"))
async def command_update_profile_handler(message: types.Message):
    """Изменение данных своего профиля"""
    msg = "Выберите что хотите изменить"
    await message.answer(msg, reply_markup=kb.update_profile_keyboard().as_markup())


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
    await callback.message.answer(msg, reply_markup=kb.cancel_inline_keyboard().as_markup())


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
            await message.answer(f"Неверный формат даты. Попробуйте еще раз")


async def confirm_delete_handler(callback: types.CallbackQuery):
    """Подтверждение удаления профиля"""
    if callback.data.split("_")[0] == "yes":
        deleted_user = db.delete_user(callback.from_user.id)
        await callback.message.answer(f'Ваш профиль "{deleted_user.user_name}" удален')
    else:
        await callback.message.answer("Отмена удаления")
    await callback.message.delete()


async def create_user_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Начало создание пользователя, инициализация FSM"""
    await state.set_state(FSMUserState.user_name)
    await callback.message.answer("Укажите ваше имя", reply_markup=kb.cancel_inline_keyboard().as_markup())


async def add_username_fsm_handler(message: types.Message, state: FSMContext):
    """Добавление username в FSM"""
    await state.update_data(user_name=message.text)
    await state.set_state(FSMUserState.birthday_date)
    await message.answer("Отлично! Теперь введите дату рождения в формате <b>ДД.ММ.ГГГГ</b>",
                         reply_markup=kb.cancel_inline_keyboard().as_markup(),
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
    await callback.message.answer("Действие отменено")
    await callback.message.delete()


def dp_register_handlers(dp: Dispatcher):
    """register all handlers"""
    # create new user
    dp.callback_query.register(create_user_handler, lambda callback: callback.data == "Создать аккаунт", StateFilter(None))
    dp.message.register(add_username_fsm_handler, FSMUserState.user_name)
    dp.message.register(add_birthday_date_handler, FSMUserState.birthday_date)

    # cancel handler
    dp.callback_query.register(cancel_handler, lambda callback: callback.data == 'cancel', StateFilter("*"))

    # delete self user confirmation
    dp.callback_query.register(confirm_delete_handler, lambda callback: callback.data.split('_')[1] == 'delete')

    # self user update profile
    dp.callback_query.register(update_profile_handler, lambda callback: callback.data.split('_')[1] == 'update')
    dp.message.register(update_profile_confirmation_handler, StateFilter(FsmUpdateUser.new_username, FsmUpdateUser.new_birthday_date))







