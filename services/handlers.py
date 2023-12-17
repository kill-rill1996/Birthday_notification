from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {message.from_user.full_name}!")


async def answer(message: Message) -> None:
    await message.answer("SOME ANSWER")


def dp_register_handlers(dp: Dispatcher):
    """register all handlers"""
    dp.message.register(answer, F.text.lower() == "привет")
