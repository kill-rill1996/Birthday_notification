import asyncio
from datetime import datetime
from aiogram import Bot
from aiogram.enums import ParseMode

import config
from config import TOKEN, DAYS_BEFORE
from database import services as db
from services import keyboards as kb

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def notify():
    """Функция автоматического оповещения за несколько дней до события"""
    all_users = db.get_all_users()
    active_events = db.get_all_events()

    for event in active_events:
        days_before_event = event.event_date - datetime.now().date()    # кол-во дней до мероприятия

        # добавление номера в событие дня рождения
        if days_before_event and event.phone == "":
            # получаем telegram_id именинника для сравнения с админами
            event_user = db.get_user_by_id(event.user_id)

            msg = f"Через 10 дней день рождения у <b>{event_user.user_name}</b>.\nВыберите номер телефона для сбора денег:"

            # отправка администраторам сообщения о выборе номера телефона для события
            for admin_tg_id in config.ADMINS:
                if admin_tg_id != event_user.telegram_id:
                    await bot.send_message(admin_tg_id,
                                           msg,
                                           parse_mode=ParseMode.HTML,
                                           reply_markup=kb.phone_choose_admin_keyboard(event.id).as_markup())
                else:
                    continue

        # if days_before_event.days in DAYS_BEFORE:    # prod version
        if days_before_event.days:    # debug version

            # составляем сообщение
            birthday_user = None
            if event.title == "birthday":
                birthday_user = db.get_user_by_id(event.user_id)
            msg = f"До <b>{'Дня рождения' if event.title == 'birthday' else 'события ' + event.title} </b>"
            if birthday_user:
                msg += f"<b>{birthday_user.user_name} {'@' + birthday_user.tg_username + ' ' if birthday_user.tg_username else ''}</b>"

            msg += f"осталось <b>{days_before_event.days}</b> дней ({datetime.strftime(event.event_date, '%d.%m.%Y')})\n\n"
            msg += f"{'Напоминаем о сборе деняк на подарок!' if event.title == 'birthday' else 'Напоминаем о сборе деняк на событие!'}"

            # рассылаем
            users_id_to_send = [payer.user_id for payer in event.payers if not payer.payment_status]
            for user_id in users_id_to_send:
                for user in all_users:
                    if user.id == user_id:
                        await bot.send_message(user.telegram_id, msg, parse_mode=ParseMode.HTML)

    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(notify())
