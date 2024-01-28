from aiogram import Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import F
from aiogram.filters import StateFilter

from services.fsm_states import storage, FSMUserState
from services.utils import parse_birthday_date

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {message.from_user.full_name}!")


async def create_user_handler(message: Message, state: FSMContext) -> None:
    """Начало создание пользователя, инициализация FSM"""
    await state.set_state(FSMUserState.user_name)
    await message.answer("Укажите имя")


async def add_username_fsm_handler(message: types.Message, state: FSMContext):
    """Добавление username в FSM"""
    await state.update_data(user_name=message.text)
    await message.answer("Отлично! Теперь введите дату рождения в формате дд.мм.гггг")
    await state.set_state(FSMUserState.birthday_date)


async def add_birthday_date_handler(message: types.Message, state: FSMContext):
    """Добавление birthday date в FSM"""
    birthday_date_parsed = parse_birthday_date(message.text)
    await state.update_data(birthday_date=birthday_date_parsed)
    await message.answer(birthday_date_parsed, type(birthday_date_parsed))
    await state.clear()


def dp_register_handlers(dp: Dispatcher):
    """register all handlers"""
    dp.message.register(create_user_handler, lambda text: F.text == "Создать аккаунт")
    dp.message.register(add_username_fsm_handler, StateFilter(FSMUserState.user_name))
    dp.message.register(add_birthday_date_handler, StateFilter(FSMUserState.birthday_date))



