from datetime import datetime
from typing import Union

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import config
from services.fsm_states import FSMGetPayment
from services.middlewares import CheckIsAdminMiddleware
from services import keyboards as kb
from database import services as db
from services.messages import all_users_admin_message, admin_event_info_message, admin_event_payer_info_message

router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(config.ADMINS))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'back')  # для возвращения с кнопки "назад"
@router.message(Command("admin"))   # для запуска с команды /admin
async def admin_panel_handler(message: Union[types.Message, types.CallbackQuery]):
    """Панель inline кнопок для администратора"""
    if type(message) == types.Message:
        await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
    else:
        await message.message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
        await message.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'events')
async def events_handler(callback: types.CallbackQuery):
    """Вывод списка актуальных событий для администратора"""
    events = db.get_all_events()
    msg = "Список всех активных событий:"
    if not events:
        msg = "Активных событий в ближайший месяц нет."
    await callback.message.answer(msg, reply_markup=kb.all_events_keyboard(events).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'delete-user')
async def delete_users_panel(callback: types.CallbackQuery):
    all_users = db.get_all_users()
    await callback.message.answer("Список всех пользователей:", reply_markup=kb.all_users_keyboard(all_users).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user')
async def delete_user(callback: types.CallbackQuery):
    """Удаление пользователя через панель администратора"""
    user_for_delete = db.get_user_by_id(int(callback.data.split('_')[1]))
    msg = f"Вы действительно хотите удалить пользователя <b>{user_for_delete.user_name} {datetime.strftime(user_for_delete.birthday_date, '%d.%m.%Y')}</b>"
    await callback.message.answer(msg, reply_markup=kb.yes_no_admin_keyboard(user_for_delete.id).as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split('_')[0] in ['yes', 'no'])
async def confirm_delete_user(callback: types.CallbackQuery):
    """Подтверждение удаления пользователя от администратора"""
    if callback.data.split("_")[0] == "yes":
        deleted_user = db.delete_user_by_id(int(callback.data.split('_')[1]))
        await callback.message.answer(f'Пользователь <b>"{deleted_user.user_name}"</b> удален', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer("Отмена удаления")
    await callback.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'users')
async def all_users(callback: types.CallbackQuery):
    """Список всех пользователей"""
    users = db.get_all_users()
    msg = all_users_admin_message(users)
    await callback.message.answer(msg, reply_markup=kb.back_admin_keyboard().as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'event')
async def event_info(callback: types.CallbackQuery):
    """Информация о конкретном событии с указанием оплат"""
    event_id = int(callback.data.split('_')[1])
    event, event_user, payer_users = db.get_event_and_user_by_event_id(event_id)
    msg = admin_event_info_message(event, event_user, payer_users)
    markup = kb.payer_info_admin_keyboard(event, payer_users)
    await callback.message.answer(msg, reply_markup=markup.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "admin-payer")
async def event_payer_info(callback: types.CallbackQuery):
    """После выбора пользователя для опплаты, предложение внести оплату"""
    payer_id = int(callback.data.split("_")[1])
    event = db.get_event_from_payer_id(payer_id)
    user = db.get_user_by_payer_id(payer_id)
    msg = admin_event_payer_info_message(user)
    await callback.message.answer(msg, reply_markup=kb.add_payment_admin_keyboard(payer_id, event.id).as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "add-pay")
async def get_pay(callback: types.CallbackQuery, state: FSMContext):
    """Запрос в FSM суммы оплаты. Начало FSM"""
    payer_id = callback.data.split("_")[1]

    await state.set_state(FSMGetPayment.amount)
    await state.update_data(payer_id=payer_id)
    msg = "Укажите сумму, которую внес пользователь"
    await callback.message.answer(msg, reply_markup=kb.cancel_inline_keyboard().as_markup(), parse_mode=ParseMode.HTML)


@router.message(FSMGetPayment.amount)
async def confirm_payment(message: types.Message, state: FSMContext):
    """Фиксирование оплаты в бд. Окончание FSM по оплате пользователем события"""
    data = await state.get_data()
    payer_id = data["payer_id"]
    user = db.get_user_by_payer_id(payer_id)

    try:
        amount = int(message.text)
        db.add_payment(payer_id, amount)
        msg = f"Оплата пользователем <b>{user.user_name}</b> в размере <b>{amount}р.</b> зафиксирована"
        await message.answer(msg, parse_mode=ParseMode.HTML)
        await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
        await state.clear()

    except ValueError:
        await message.answer("Введите пожалуйста число без букв и иных символов", reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'cancel', StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Отмена всех FSM и удаление последнего сообщения"""
    await state.clear()
    await callback.message.answer("Действие отменено")
    await callback.message.delete()


