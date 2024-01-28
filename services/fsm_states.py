from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class FSMUserState(StatesGroup):
    user_name = State()
    birthday_date = State()

