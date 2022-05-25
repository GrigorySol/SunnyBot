from datetime import datetime, timedelta
from time import sleep

from config import VIP
from loader import bot
import schedule

from database_control.db_singer import get_singers_id_by_event
from database_control.db_event import search_event_by_date
from keyboards.inline.choice_buttons import callback_buttons
from misc.messages import attendance_dictionary as at_d, event_dictionary as ev_d, reminder_dictionary as rem_d


def schedule_pending():
    while True:
        print(f"schedule pending {datetime.now()}")
        schedule.run_pending()
        sleep(50)


def check_event_date():
    """Check if there is an event in one week, one day or day to day in the database."""

    current_date = datetime.now().date()
    before_week = current_date + timedelta(weeks=1)
    before_day = current_date + timedelta(days=1)

    today_events = search_event_by_date(current_date)
    day_events = search_event_by_date(before_day)
    week_events = search_event_by_date(before_week)

    if today_events:
        for event_id, _, event_name, event_time in today_events:
            print(f"Events for today:\n{event_name}")
            event_reminder(event_id, event_name, "Cегодня", event_time)
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

    call_config = "singer_attendance"
    data = [
        (text, f"{call_config}:edit:{event_id}:{i}")
        for i, text in enumerate(at_d.set_attendance_text_tuple)
    ]

    msg_date = f"{event_date} в {event_time}"

    if event_date != "Cегодня":
        year, month, day = event_date.split("-")
        msg_date = f"{int(day)} {ev_d.chosen_months_text_tuple[int(month) - 1]} в {event_time}"

    msg = f"{msg_date} {rem_d.will_be_text} '{event_name}'.\n" \
          f"{rem_d.info_in_calendar_text}\n" \
          f"{rem_d.select_attendance_text}"
    markup = callback_buttons(data)

    for singer_id in get_singers_id_by_event(event_id):
        try:
            print(f"Message for singer id {singer_id[0]}")
            bot.send_message(singer_id[0], msg, reply_markup=markup)
        except Exception as e:
            print(f"{e}\n{singer_id[0]} not exists")


def database_sender():
    """Send database file to the VIP telegram_id"""

    print("DATABASE file sent")
    file = open("database_control/sunny_bot.db", 'rb')
    bot.send_document(VIP, file)
    bot.send_message(VIP, "Отправлено?")
    file.close()


schedule.every().day.at("01:27").do(database_sender)
schedule.every().day.at("07:15").do(check_event_date)
