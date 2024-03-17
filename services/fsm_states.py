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
    phone_to_pay = State()


class FSMDeleteEvent(StatesGroup):
    # pick_event = State()
    confirmation = State()


class FSMUpdateEventDate(StatesGroup):
    event_date = State()


class FSMUpdateEventTitle(StatesGroup):
    event_title = State()


class FSMUpdateEventPhone(StatesGroup):
    phone_number = State()
