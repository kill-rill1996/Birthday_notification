from datetime import datetime
from typing import Union

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import config
from services.errors import DateValidationError, DatePeriodError
from services.utils import check_validation_date, send_message
from services.fsm_states import FSMGetPayment, FSMAddEvent, FSMDeleteEvent
from services.middlewares import CheckIsAdminMiddleware
from services import keyboards as kb
from database import services as db
from services.messages import all_users_admin_message, admin_event_info_message, admin_event_payer_info_message, \
    admin_successful_create_event_birthday, admin_event_delete_confirmation

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
    events = db.get_all_events(all_events=False)
    msg = "Список всех активных событий:"
    if not events:
        msg = "Активных событий в ближайший месяц нет."
    await callback.message.answer(msg, reply_markup=kb.all_events_keyboard(events).as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "admin" and callback.data.split("_")[1] == "delete-event")
async def delete_events_admin_panel(callback: types.CallbackQuery, state: FSMContext):
    """Удаление события через панель администратора, получение всех событий. Старт FSMDeleteEvent"""
    events = db.get_all_events(all_events=False)
    await state.set_state(FSMDeleteEvent.pick_event)
    await callback.message.answer("Выберите событие, которое хотите удалить:",
                                  reply_markup=kb.all_events_keyboard_to_delete(events).as_markup())


@router.callback_query(FSMDeleteEvent.pick_event, lambda callback: callback.data.split("_")[0] == "event")
async def delete_event_admin_confirmation(callback: types.CallbackQuery, state: FSMContext):
    """Выбор события для удаления"""
    event_id = int(callback.data.split("_")[1])
    event = db.get_event_by_event_id(event_id)
    await state.set_state(FSMDeleteEvent.confirmation)
    await callback.message.answer(admin_event_delete_confirmation(event),
                                  reply_markup=kb.yes_no_admin_keyboard(event_id).as_markup())


@router.callback_query(FSMDeleteEvent.confirmation)
async def delete_event(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.split("_")[0] == "yes":
        event_id = int(callback.data.split("_")[1])
        db.hide_event(event_id)
        await callback.message.answer("Событие удалено!")
    else:
        await callback.message.answer("Отмена удаления")
    await state.clear()
    await callback.message.delete()


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'delete-user')
async def delete_users_panel(callback: types.CallbackQuery):
    all_users = db.get_all_users()
    await callback.message.answer("Выберите пользователя, которого хотите удалить:", reply_markup=kb.all_users_keyboard_to_delete(all_users).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user-delete')
async def delete_user(callback: types.CallbackQuery):
    """Удаление пользователя через панель администратора"""
    user_for_delete = db.get_user_by_id(int(callback.data.split('_')[1]))
    msg = f"Вы действительно хотите удалить пользователя <b>{user_for_delete.user_name} {datetime.strftime(user_for_delete.birthday_date, '%d.%m.%Y')}</b>"
    await callback.message.answer(msg, reply_markup=kb.yes_no_admin_keyboard(user_for_delete.id).as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: (callback.data.split('_')[0] in ['yes', 'no']) and
                                        (callback.data.split('_')[1] != "delete"))
async def confirm_delete_user(callback: types.CallbackQuery):
    """Подтверждение удаления пользователя от администратора"""
    if callback.data.split("_")[0] == "yes":
        print(callback.data.split('_')[1])
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
    msg = "Напишите сумму, которую внес пользователь или выберите из предложенных"
    await callback.message.answer(msg, reply_markup=kb.admin_pay_keyboard().as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "paid", FSMGetPayment.amount)
@router.message(FSMGetPayment.amount)
async def confirm_payment(message: types.Message, state: FSMContext):
    """Фиксирование оплаты в бд. Окончание FSM по оплате пользователем события"""
    data = await state.get_data()
    payer_id = data["payer_id"]
    user = db.get_user_by_payer_id(payer_id)

    if type(message) == types.Message:
        try:
            amount = int(message.text)
            db.add_payment(payer_id, amount)
            msg = f"Оплата пользователем <b>{user.user_name}</b> в размере <b>{amount}р.</b> зафиксирована"
            await message.answer(msg, parse_mode=ParseMode.HTML)
            await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
            await state.clear()
        except ValueError:
            await message.answer("Введите пожалуйста число без букв и иных символов", reply_markup=kb.cancel_inline_keyboard().as_markup())
    else:
        amount = int(message.data.split("_")[1])
        db.add_payment(payer_id, amount)
        msg = f"Оплата пользователем <b>{user.user_name}</b> в размере <b>{amount}р.</b> зафиксирована"
        await message.message.answer(msg, parse_mode=ParseMode.HTML)
        await message.message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
        await state.clear()


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'add-event')
async def create_new_event_panel(callback: types.CallbackQuery):
    """Создание события через клавиатуру администратора"""
    await callback.message.answer("Выберите тип события, которое хотите добавить", reply_markup=kb.add_event_admin_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'add-event')
async def create_new_event(callback: types.CallbackQuery, state: FSMContext):
    """Начало создания события. Начало FSM (если не др)"""
    if callback.data.split('_')[1] == 'other':
        await state.set_state(FSMAddEvent.title)
        await callback.message.answer('Введите название события (например "корпоратив")',
                                      reply_markup=kb.cancel_inline_keyboard().as_markup())
    else:
        users = db.get_all_users()
        await callback.message.answer('Выберите пользователя, чей день рождения хотите добавить в ближайшие события',
                                      reply_markup=kb.all_users_keyboard_for_event_creating(users).as_markup())


@router.message(FSMAddEvent.title)
async def create_title_new_event(message: types.Message, state: FSMContext):
    """Создание названия события и переход на state event_date"""
    await state.update_data(title=message.text)
    await state.set_state(FSMAddEvent.event_date)
    await message.answer("Введите дату события в формате <b>ДД.ММ.ГГГГ</b>",
                         parse_mode=ParseMode.HTML, reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.message(FSMAddEvent.event_date)
async def create_event_date_new_event(message: types.Message, state: FSMContext):
    try:
        event_date_parsed = check_validation_date(message.text)
        await state.update_data(event_date=event_date_parsed)
        await state.set_state(FSMAddEvent.except_user)

        users = db.get_all_users()
        await message.answer(f"Выберите кто из пользователей <b>НЕ</b> должен знать о событии:",
                             reply_markup=kb.all_users_keyboard_for_except_from_event(users).as_markup(),
                             parse_mode=ParseMode.HTML)
    except DateValidationError:
        await message.answer(f"Неверный формат даты. Попробуйте еще раз")
    except DatePeriodError:
        await message.answer(f"Неверно указан год события (допускается текущий год и следующий). Попробуйте еще раз")


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user-event-except',
                       FSMAddEvent.except_user)
async def create_event_excepting_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split("_")[1]
    if user_id == "all":
        await state.update_data(except_user=None)
    else:
        await state.update_data(except_user=int(user_id))
    data = await state.get_data()

    db.create_event_and_payers(user_id=data['except_user'], birthday_date=data['event_date'], title=data['title'])

    await callback.message.answer(f"Событие <b>{data['title']} {datetime.strftime(data['event_date'], '%d.%m.%Y')}</b> успешно создано!",
                                  parse_mode=ParseMode.HTML)
    await callback.message.delete()
    await state.clear()


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user-event')
async def create_new_event(callback: types.CallbackQuery):
    """Создание события дня рождения для пользователя через панель администратора"""
    user = db.get_user_by_id(int(callback.data.split("_")[1]))
    events = db.get_all_events_birthday()
    if user.id not in [event.user_id for event in events]:
        db.create_event_and_payers(user.id, user.birthday_date)
        msg = admin_successful_create_event_birthday(user)
    else:
        msg = f'<b>Ошибка</b>. Событие "День рождения пользователя {user.user_name}" уже существует!'
    await callback.message.answer(msg, parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split("_")[1] == "ping")
async def notify_users_menu(callback: types.CallbackQuery):
    """Оповещение всех пользователей о ближайших событиях с клавиатуры админа"""
    users_to_ping, events = db.get_all_users_and_events_exclude_admin(callback.from_user.id)
    keyboard = kb.all_events_to_ping_keyboard(events)
    await callback.message.answer(f"Выберите событие о котором хотите оповестить пользователей", reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'cancel', StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Отмена всех FSM и удаление последнего сообщения"""
    await state.clear()
    await callback.message.answer("Действие отменено")
    await callback.message.delete()