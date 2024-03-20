import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.enums import ParseMode

import config
from config import TOKEN, DAYS_BEFORE
from database import services as db
from database import tables
from services import keyboards as kb

bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


async def notify():
    """Функция автоматического оповещения за несколько дней до события"""
    all_users = db.get_all_users()
    active_events = db.get_all_events()

    for event in active_events:
        days_before_event = event.event_date - datetime.now().date()    # кол-во дней до мероприятия

        # добавление номера в событие дня рождения
        if days_before_event.days <= config.DAYS_BEFORE_PHONE and event.phone == "":
            # получаем telegram_id именинника для сравнения с админами
            event_user = db.get_user_by_id(event.user_id)

            msg = f"Через 10 дней день рождения у <b>{event_user.user_name} {datetime.strftime(event.event_date, '%d.%m.%Y')}</b>.\nВыберите номер телефона для сбора денег:"

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
        if days_before_event:    # debug version

            # составляем сообщение
            birthday_user = None
            if event.title == "birthday":
                birthday_user = db.get_user_by_id(event.user_id)
            msg = f"До <b>{'Дня рождения' if event.title == 'birthday' else 'события ' + event.title} </b>"
            if birthday_user:
                msg += f"<b>{birthday_user.user_name} {'@' + birthday_user.tg_username + ' ' if birthday_user.tg_username else ''}</b>"

            msg += f"осталось <b>{days_before_event.days}</b> дней ({datetime.strftime(event.event_date, '%d.%m.%Y')})\n\n"

            # рассылаем
            for payer in event.payers:
                sub = create_notify_sub_msg(payer, event)
                for user in all_users:
                    if user.id == payer.user_id:
                        await bot.send_message(user.telegram_id, msg + sub, parse_mode=ParseMode.HTML)

    await bot.session.close()


def create_notify_sub_msg(payer: tables.Payer, event: tables.Event) -> str:
    """Создание конца сообщения в зависимости от оплаты или не оплаты"""
    if payer.payment_status:
        return f"✅ Событие оплачено ({payer.summ}р.)"
    else:
        sub_msg = f"{'Напоминаем о сборе деняк на подарок!' if event.title == 'birthday' else 'Напоминаем о сборе деняк на событие!'}\n\n" \
               f"❌ Событие не оплачено\n"
        if event.phone:
            sub_msg += f"Телефона для перевода денег \n{event.phone}"

        return sub_msg


if __name__ == "__main__":
    asyncio.run(notify())
