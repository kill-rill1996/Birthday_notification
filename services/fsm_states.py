from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


storage = MemoryStorage()


class FSMUserState(StatesGroup):
    user_name = State()
    birthday_date = State()


class FsmUpdateUser(StatesGroup):
    new_username = State()
    new_birthday_date = State()


class FSMGetPayment(StatesGroup):
    amount = State()


class FSMAddEvent(StatesGroup):
    title = State()
    event_date = State()
    except_user = State()


class FSMDeleteEvent(StatesGroup):
    pick_event = State()
    confirmation = State()
