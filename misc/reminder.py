from datetime import datetime, timedelta
from time import sleep
import inspect

from config import VIP
from loader import bot, log
import schedule

from database_control.db_singer import get_telegram_id_attend_by_event
from database_control.db_event import search_event_by_date, search_location_by_event_id
from keyboards.inline.choice_buttons import buttons_markup
from misc import dicts, keys


def schedule_pending():
    while True:
        schedule.run_pending()
        sleep(50)


def check_event_date():
    """Check if there is an event in one week, one day or day to day in the database."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\n")

    current_date = datetime.now().date()
    before_day = current_date + timedelta(days=1)
    before_week = current_date + timedelta(weeks=1)

    today_events = search_event_by_date(current_date)
    day_events = search_event_by_date(before_day)
    week_events = search_event_by_date(before_week)

    if not today_events and not day_events and not week_events:
        print("Nothing to send")
        return
    if today_events:
        for event_id, _, event_name, event_time in today_events:
            print(f"Events for today:\n{event_name}")
            event_reminder(event_id, event_name, dicts.attends.today_text, event_time)
    if day_events:
        for event_id, _, event_name, event_time in day_events:
            print(f"Events in one day:\n{event_name}")
            event_reminder(event_id, event_name, f"{before_day}", event_time)
    if week_events:
        for event_id, _, event_name, event_time in week_events:
            print(f"Events in one week:\n{event_name}")
            event_reminder(event_id, event_name, f"{before_week}", event_time)


def event_reminder(event_id: int, event_name: str, event_date: str, event_time: str):
    """Create and send a message to all participating singers."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\n")

    location = search_location_by_event_id(event_id)
    location_name = "Не определена." if not location else location[0]

    call_config = dicts.call_dic.singer_attendance_text
    data = [
        {"text": text, "callback_data": f"{call_config}:edit:{event_id}:{i}"}
        for i, text in enumerate(dicts.attends.set_attendance_text_tuple)
    ]

    msg_date = f"{event_date} в {event_time}"

    if event_date != dicts.attends.today_text:
        year, month, day = event_date.split("-")
        msg_date = f"{int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]} в {event_time}"

    markup = buttons_markup(data)
    count = 0

    for telegram_id, attendance in get_telegram_id_attend_by_event(event_id):
        try:
            msg = f"{msg_date}:\n{event_name}\n{dicts.events.location_text} {location_name}\n" \
                  f"{dicts.reminds.info_in_calendar_text}\n"

            if attendance == 1 and event_date == dicts.attends.today_text:
                msg += f"\n{dicts.attends.chosen_attendance_text}\n" \
                       f"{dicts.attends.set_attendance_text_tuple[1]}\n" \
                       f"\n{dicts.attends.wanna_change_text}"
                bot.send_message(telegram_id, msg)
                count += 1

            elif attendance == 2:
                msg += f"{dicts.reminds.select_attendance_text}"
                bot.send_message(telegram_id, msg, reply_markup=markup)
                count += 1

        except Exception as e:
            print(f"{e}\n\n❗️ {telegram_id} not exists ❗️\n\n")

    print(f"Sent {count} messages")


def database_sender():
    """Send database file to the VIP telegram_id and clear ButtonKeeper _btn_ids"""

    print(f"DATABASE file sent at {datetime.now()}")
    file = open("database_control/sunny_bot.db", 'rb')
    bot.send_document(VIP, file)
    bot.send_message(VIP, f"database backup {datetime.now()}")
    file.close()

    keys.buttons.ButtonsKeeper.clear_saved_ids()


schedule.every().day.at("01:27").do(database_sender)
schedule.every().day.at("07:15").do(check_event_date)
