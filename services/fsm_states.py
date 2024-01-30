from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class FSMUserState(StatesGroup):
    user_name = State()
    birthday_date = State()


class FsmUpdateUser(StatesGroup):
    new_username = State()
    new_birthday_date = State()
