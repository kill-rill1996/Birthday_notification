from datetime import datetime
from typing import Union

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import config
from services.errors import DateValidationError, DatePeriodError, WrongDateError, PhoneNumberError
from services.utils import check_validation_date, validate_phone_number, parse_phone_number
from services.fsm_states import FSMGetPayment, FSMAddEvent, FSMDeleteEvent, FSMUpdateEventDate, FSMUpdateEventTitle, \
    FSMUpdateEventPhone, FSMPaymentInfo, FSMUpdateEventBank
from services.middlewares import CheckIsAdminMiddleware
from services import keyboards as kb
from database import services as db
from services.messages import all_users_admin_message, admin_event_info_message, admin_event_payer_info_message, \
    admin_successful_create_event_birthday, admin_event_delete_confirmation

router = Router()
router.message.middleware.register(CheckIsAdminMiddleware(config.ADMINS))


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'back' or callback.data.split('_')[1] == 'back-b')  # для возвращения с кнопки "назад"
@router.message(Command("admin"))   # для запуска с команды /admin
async def admin_panel_handler(message: Union[types.Message, types.CallbackQuery]):
    """Панель inline кнопок для администратора"""
    if type(message) == types.Message:
        await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
    else:
        if message.data.split('_')[1] == 'back-b':
            await message.message.edit_text("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())
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
    await callback.message.edit_text(msg, reply_markup=kb.all_events_keyboard(events).as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "admin" and callback.data.split("_")[1] == "delete-event")
async def delete_events_admin_panel(callback: types.CallbackQuery):
    """Удаление события через панель администратора, получение всех событий."""
    events = db.get_all_events()
    await callback.message.edit_text("Выберите событие, которое хотите удалить:",
                                     reply_markup=kb.all_events_keyboard_to_delete(events).as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "deleteEvent")
async def delete_event_admin_confirmation(callback: types.CallbackQuery, state: FSMContext):
    """Выбор события для удаления"""
    event_id = int(callback.data.split("_")[1])
    event = db.get_event_by_event_id(event_id)
    await state.set_state(FSMDeleteEvent.confirmation)
    await callback.message.edit_text(admin_event_delete_confirmation(event),
                                  reply_markup=kb.yes_no_admin_keyboard(event_id).as_markup())


@router.callback_query(FSMDeleteEvent.confirmation)
async def delete_event(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.split("_")[0] == "yes":
        event_id = int(callback.data.split("_")[1])
        db.hide_event(event_id)
        await callback.message.edit_text("Событие удалено!")
    else:
        await callback.message.edit_text("Отмена удаления.")
    await state.clear()
    await callback.message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'admin' and callback.data.split('_')[1] == 'delete-user')
async def delete_users_panel(callback: types.CallbackQuery):
    all_users = db.get_all_users()
    await callback.message.edit_text("Выберите пользователя, которого хотите удалить:",
                                     reply_markup=kb.all_users_keyboard_to_delete(all_users).as_markup())


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
    await callback.message.edit_text(msg, reply_markup=kb.back_admin_keyboard().as_markup(), parse_mode=ParseMode.HTML)


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
async def create_new_event_panel(callback: types.CallbackQuery, state: FSMContext):
    """Создание события через клавиатуру администратора"""
    await state.set_state(FSMAddEvent.title)
    await callback.message.answer('Введите название события (например "корпоратив")',
                                  reply_markup=kb.cancel_inline_keyboard().as_markup())


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
        await message.answer(f"Неверно указан год события (допускается текущий год или следующий). Попробуйте еще раз")


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'user-event-except',
                       FSMAddEvent.except_user)
async def create_event_excepting_user(callback: types.CallbackQuery, state: FSMContext):
    """Добавление номера телефона к событию"""
    user_id = callback.data.split("_")[1]
    if user_id == "all":
        await state.update_data(except_user=None)
    else:
        await state.update_data(except_user=int(user_id))

    await callback.message.answer(f"Выберите номер телефона, по которому будет производиться оплата, из списка "
                                  f"или введите в ручную в формате 8ХХХХХХХХХХ",
                                  reply_markup=kb.phone_choose_keyboard().as_markup())

    await callback.message.delete()
    await state.set_state(FSMAddEvent.phone_to_pay)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "phone", FSMAddEvent.phone_to_pay)
@router.message(FSMAddEvent.phone_to_pay)
async def create_event_phone(message: types.Message, state: FSMContext):
    """Добавление номера телефона по которому переводить деньги"""
    if type(message) == types.Message:
        phone = message.text
        try:
            validate_phone_number(phone)
            phone = parse_phone_number(phone)

            await state.update_data(phone=phone)

            await message.answer("Выберите банк для перевода денег из списка или отправьте сообщением",
                                    reply_markup=kb.bank_choose_admin_keyboard(with_cancel=True).as_markup())

            await state.set_state(FSMAddEvent.bank)

        except PhoneNumberError:
            await message.answer(f"Неверный формат номера телефона. Попробуйте еще раз",
                                 reply_markup=kb.phone_choose_keyboard().as_markup())
    else:
        phone = message.data.split("_")[1]

        await state.update_data(phone=phone)

        await message.message.edit_text("Выберите банк для перевода денег из списка или отправьте сообщением",
                                        reply_markup=kb.bank_choose_admin_keyboard(with_cancel=True).as_markup())

        await state.set_state(FSMAddEvent.bank)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "birthday-bank-info", FSMAddEvent.bank)
@router.message(FSMAddEvent.bank)
async def create_event_bank(message: types.Message | types.CallbackQuery, state: FSMContext):
    """Добавление номера телефона по которому переводить деньги"""
    data = await state.get_data()

    if type(message) == types.Message:
        bank_info = message.text
    else:
        bank_info = message.data.split("_")[1]

    if bank_info == "tinkoff":
        bank = "Тинькофф"
    elif bank_info == "vtb":
        bank = "ВТБ"
    elif bank_info == "alfabank":
        bank = "Альфа-Банк"
    elif bank_info == "sberbank":
        bank = "СберБанк"
    else:
        bank = bank_info

    db.create_event_and_payers(user_id=data['except_user'], birthday_date=data['event_date'],
                               title=data['title'], phone=data["phone"], bank=bank)
    await state.clear()

    if type(message) == types.Message:
        await message.answer(
            f"Событие <b>{data['title']} {datetime.strftime(data['event_date'], '%d.%m.%Y')}</b> успешно создано!",
            parse_mode=ParseMode.HTML)

        await message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())

    else:
        await message.message.answer(
            f"Событие <b>{data['title']} {datetime.strftime(data['event_date'], '%d.%m.%Y')}</b> успешно создано!",
            parse_mode=ParseMode.HTML)

        await message.message.answer("Выберите действие", reply_markup=kb.admins_keyboard().as_markup())


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
    await callback.message.edit_text(f"Выберите событие, о котором хотите оповестить пользователей",
                                     reply_markup=keyboard.as_markup(), parse_mode=ParseMode.HTML)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "update-event-date")
async def update_event_date_start(callback: types.CallbackQuery, state: FSMContext):
    """Изменение даты события с панели администратора, начало FSMUpdateEvent"""
    event_id = callback.data.split("_")[1]
    await state.set_state(FSMUpdateEventDate.event_date)
    await state.update_data(event_id=event_id)
    await callback.message.answer("Введите дату события в формате <b>ДД.ММ.ГГГГ</b>",
                                  parse_mode=ParseMode.HTML, reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.message(FSMUpdateEventDate.event_date)
async def update_event_date_finish(message: types.Message, state: FSMContext):
    """Изменение даты события"""
    try:
        new_event_date = check_validation_date(message.text)

        if new_event_date < datetime.now().date():
            raise WrongDateError

        data = await state.get_data()
        event_id = data["event_id"]
        updated_event = db.update_event_date(event_id, new_event_date)

        # если событие др
        if updated_event.title == "birthday":
            user = db.get_user_by_id(updated_event.user_id)

            events = db.get_all_events()
            await message.answer(f"Дата события \"День рождения пользователя <b>{user.user_name}</b>\" изменена "
                                 f"на <b>{datetime.strftime(updated_event.event_date, '%d.%m.%Y')}</b>")

        # если событие другое
        else:
            events = db.get_all_events()
            await message.answer(f"Дата события <b>\"{updated_event.title}\"</b> изменена "
                                 f"на <b>{datetime.strftime(updated_event.event_date, '%d.%m.%Y')}</b>")

        await message.answer(f"Список активных событий", reply_markup=kb.all_events_keyboard(events).as_markup())

        await state.clear()

    except DateValidationError:
        await message.answer(f"Неверный формат даты. Попробуйте еще раз")
    except DatePeriodError:
        await message.answer(f"Неверно указан год события (допускается текущий год и следующий). Попробуйте еще раз")
    except WrongDateError:
        await message.answer("Дата не может быть раньше сегодняшней. Попробуйте еще раз")


@router.callback_query(lambda callback: callback.data.split("_")[0] == "update-event-phone")
async def update_event_phone_number_start(callback: types.CallbackQuery, state: FSMContext):
    """Изменение номера телефона для события"""
    event_id = callback.data.split("_")[1]
    await state.update_data(event_id=event_id)

    await callback.message.answer(f"Выберите номер телефона, по которому будет производиться оплата, из списка "
                                  f"или введите в ручную в формате 8ХХХХХХХХХХ",
                                  reply_markup=kb.phone_choose_keyboard().as_markup())

    await state.set_state(FSMUpdateEventPhone.phone_number)


@router.callback_query(lambda callback: callback.data.split("_")[0] == "phone", FSMUpdateEventPhone.phone_number)
@router.message(FSMUpdateEventPhone.phone_number)
async def update_event_phone_number_finish(message: types.Message, state: FSMContext):
    """Изменение номера телефона по которому переводить деньги"""
    if type(message) == types.Message:
        phone = message.text
        try:
            validate_phone_number(phone)
            phone = parse_phone_number(phone)

            data = await state.get_data()

            db.update_event_phone(event_id=data["event_id"], new_phone=phone)

            await message.answer(f"Номер телефона для события изменен на <b>{phone}</b>")

            events = db.get_all_events()
            await message.answer(f"Список активных событий", reply_markup=kb.all_events_keyboard(events).as_markup())

            await state.clear()

        except PhoneNumberError:
            await message.answer(f"Неверный формат номера телефона. Попробуйте еще раз",
                                 reply_markup=kb.phone_choose_keyboard().as_markup())
    else:
        phone = message.data.split("_")[1]

        data = await state.get_data()

        db.update_event_phone(event_id=data["event_id"], new_phone=phone)

        await message.message.answer(f"Номер телефона для события изменен на <b>{phone}</b>")

        events = db.get_all_events()
        await message.message.answer(f"Список активных событий", reply_markup=kb.all_events_keyboard(events).as_markup())

        await state.clear()


@router.callback_query(lambda callback: callback.data.split("_")[0] == "update-event-title")
async def update_event_title_start(callback: types.CallbackQuery, state: FSMContext):
    """Изменение названия события с панели администратора, начало FSMUpdateEventTitle"""
    event_id = callback.data.split("_")[1]
    await state.set_state(FSMUpdateEventTitle.event_title)
    await state.update_data(event_id=event_id)
    await callback.message.answer("Введите новое название события", reply_markup=kb.cancel_inline_keyboard().as_markup())


@router.message(FSMUpdateEventTitle.event_title)
async def update_event_title_finish(message: types.Message, state: FSMContext):
    """Изменение названия события, окончание FSMUpdateEventTitle"""
    data = await state.get_data()
    event_id = data["event_id"]
    new_title = message.text

    db.update_event_title(event_id, new_title)
    events = db.get_all_events()

    await message.answer(f"Название события изменено на <b>{new_title}</b>")
    await message.answer(f"Список активных событий", reply_markup=kb.all_events_keyboard(events).as_markup())
    await state.clear()


@router.callback_query(lambda callback: callback.data.split("_")[0] == "update-event-bank")
async def update_event_bank_start(callback: types.CallbackQuery, state: FSMContext):
    """Изменение названия события с панели администратора, начало FSMUpdateEventTitle"""
    event_id = callback.data.split("_")[1]
    await state.set_state(FSMUpdateEventBank.bank)
    await state.update_data(event_id=event_id)
    await callback.message.edit_text("Введите новое название банка или выберите из списка",
                                     reply_markup=kb.bank_choose_admin_keyboard().as_markup())


@router.callback_query(lambda callback: callback.data.split("_")[0] == "birthday-bank-info", FSMUpdateEventBank.bank)
@router.message(FSMUpdateEventBank.bank)
async def update_event_bank_finish(message: types.Message, state: FSMContext):
    """Изменение банка на который переводить деньги"""
    if type(message) == types.Message:
        bank_info = message.text
    else:
        bank_info = message.data.split("_")[1]

    if bank_info == "tinkoff":
        bank = "Тинькофф"
    elif bank_info == "vtb":
        bank = "ВТБ"
    elif bank_info == "alfabank":
        bank = "Альфа-Банк"
    elif bank_info == "sberbank":
        bank = "СберБанк"
    else:
        bank = bank_info

    data = await state.get_data()
    event_id = data["event_id"]

    db.update_event_bank(int(event_id), bank)
    events = db.get_all_events()
    await state.clear()

    if type(message) == types.Message:
        await message.answer(f"Банк для события изменен на <b>{bank}</b>")
        await message.answer(f"Список активных событий", reply_markup=kb.all_events_keyboard(events).as_markup())
    else:
        await message.message.edit_text(f"Банк для события изменен на <b>{bank}</b>")
        await message.message.answer(f"Список активных событий",
                                     reply_markup=kb.all_events_keyboard(events).as_markup())


@router.callback_query(lambda callback: callback.data.split('_')[0] == 'birthday-phone')
async def choose_payment_info_for_birthday_start(callback: types.CallbackQuery, state: FSMContext):
    """Выбор телефона для события типа 'birthday' (только для администраторов)"""
    event_id = int(callback.data.split('_')[1])
    phone = callback.data.split('_')[2]
    event = db.get_event_by_event_id(event_id)
    event_user = db.get_user_by_id(event.user_id)

    if event.phone == "":
        await state.set_state(FSMPaymentInfo.bank_info)
        await state.update_data(event_id=event_id)

        db.update_event_phone(event_id, phone)
        await callback.message.edit_text(
            f'Телефон <b>{phone}</b> успешно добавлен для дня рождения {event_user.user_name}.\n'
            f'Выберите банк для сбора денег из списка или отправьте название сообщением:',
            reply_markup=kb.bank_choose_admin_keyboard().as_markup(),
            parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text(f'Телефон <b>{event.phone}</b> уже добавлен в день рождения {event_user.user_name} другим администратором.\nВы можете изменить телефон события во вкладке "События"',
                                      parse_mode=ParseMode.HTML)


@router.callback_query(lambda message: message.data.split("_")[0] == "birthday-bank-info", FSMPaymentInfo.bank_info)
@router.message(FSMPaymentInfo.bank_info)
async def choose_payment_info_for_birthday_finish(message: types.Message, state: FSMContext):
    """Выбор банка для события типа 'birthday' (только для администраторов)"""
    data = await state.get_data()
    event_id = data["event_id"]

    event = db.get_event_by_event_id(event_id)
    event_user = db.get_user_by_id(event.user_id)

    if type(message) == types.Message:
        bank_info = message.text

        if bank_info == "tinkoff":
            bank = "Тинькофф"
        elif bank_info == "vtb":
            bank = "ВТБ"
        elif bank_info == "alfabank":
            bank = "Альфа-Банк"
        elif bank_info == "sberbank":
            bank = "СберБанк"
        else:
            bank = bank_info

        if event.bank == "":
            db.update_event_bank(event_id, bank)
            await message.edit_text(
                f'Банк "<b>{bank}</b>" успешно добавлен для дня рождения {event_user.user_name}.',
                parse_mode=ParseMode.HTML)
        else:
            await message.edit_text(f'Банк <b>{event.bank}</b> уже добавлен в день рождения '
                                 f'{event_user.user_name} другим администратором.\n'
                                 f'Вы можете изменить банк события во вкладке "События"',
                                 parse_mode=ParseMode.HTML)
    else:
        bank_info = message.data.split("_")[1]

        if bank_info == "tinkoff":
            bank = "Тинькофф"
        elif bank_info == "vtb":
            bank = "ВТБ"
        elif bank_info == "alfabank":
            bank = "Альфа-Банк"
        elif bank_info == "sberbank":
            bank = "СберБанк"
        else:
            bank = bank_info

        if event.bank == "":
            db.update_event_bank(event_id, bank)
            await message.message.edit_text(
                f'Банк "<b>{bank}</b>" успешно добавлен для дня рождения {event_user.user_name}.',
                parse_mode=ParseMode.HTML)
        else:
            await message.message.edit_text(f'Банк <b>{event.bank}</b> уже добавлен в день рождения '
                                         f'{event_user.user_name} другим администратором.\n'
                                         f'Вы можете изменить банк события во вкладке "События"',
                                         parse_mode=ParseMode.HTML)

    await state.clear()


@router.callback_query(lambda callback: callback.data.split('_')[1] == 'cancel', StateFilter("*"))
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    """Отмена всех FSM и удаление последнего сообщения"""
    await state.clear()
    await callback.message.answer("Действие отменено")
    await callback.message.delete()