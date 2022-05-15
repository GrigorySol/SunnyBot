from datetime import datetime, date, timedelta
from loader import bot
from database_control import db_event, db_attendance
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import calendar_zoom, calendar_factory, \
    calendar_data, location_callback, repeat_callback, interval_callback, show_attendance_callback

from keyboards.inline.calendar_buttons import generate_calendar_days, generate_calendar_months, EMTPY_FIELD

from keyboards.inline.choice_buttons import choose_location_markup, callback_buttons, \
    repeat_buttons, add_concert_songs_buttons, message_buttons
from misc.edit_functions import enter_new_event_time
from misc.messages import event_dictionary as ev_d, changes_dictionary as ch_d, singer_dictionary as sin_d


class EventData:
    def __init__(self):
        self.event_id = None
        self.event_name = "Репетиция"
        self.date = None
        self.time = None
        self.is_in_progress = False


class LocationData:
    def __init__(self):
        self.url = None


event_data = EventData()
location_data = LocationData()


@bot.message_handler(commands=['calendar'])
def calendar_command_handler(message: Message):
    """Show calendar buttons"""
    now = date.today()
    event_id = "0"
    bot.send_message(message.chat.id, ev_d.set_event_date_text,
                     reply_markup=generate_calendar_days(now.year, now.month, int(event_id)))


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter(event_id="0"))
def calendar_show_event_handler(call: CallbackQuery):
    """Show events for the chosen day."""

    print(f"calendar_datetime_handler {call.data}")
    _, event_id, year, month, day, _id = call.data.split(":")
    # Show all events for this day
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}%"
    events = db_event.search_event_by_date(event_data.date)
    call_config = "event"
    data = []

    if not events:
        bot.send_message(call.message.chat.id, ev_d.no_event_text)
        return
    for event in events:
        event_time = event[4][1][0:5]
        data.append((f"{event[2]} {event_time}", f"{call_config}:{event[0]}"))

    text = f"{ev_d.current_events_text} {day} {ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года:"
    bot.send_message(call.message.chat.id, text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter(event_id="4"))
def edit_event_date_handler(call: CallbackQuery):
    """Edit date for the chosen event"""

    print(f"calendar_datetime_handler {call.data}")
    _, event_id, year, month, day, _id = call.data.split(":")
    # Edit event date
    msg = f"Вы выбрали {ev_d.events_to_add_text_tuple[event_id]} на {day} " \
          f"{ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года.\n{ev_d.set_event_time_text}"
    bot.register_next_step_handler(msg, enter_new_event_time, _id, year, month, day)


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter())
def add_event_time_handler(call: CallbackQuery):
    """Add time for a new event"""

    print(f"calendar_datetime_handler {call.data}")
    _, event_id, year, month, day, _id = call.data.split(":")
    # Continue to add an event
    event_data.is_in_progress = True
    event_data.event_id = int(event_id)
    event_data.event_name = ev_d.events_to_add_text_tuple[event_data.event_id]
    msg = f"Вы выбрали {ev_d.events_to_add_text_tuple[event_data.event_id]} на {day} " \
          f"{ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года.\n{ev_d.set_event_time_text}"
    msg_data = bot.send_message(call.message.chat.id, msg)
    bot.register_next_step_handler(msg_data, add_time_for_event)


def add_time_for_event(message: Message):
    """Get time from the input and ask to name the event or set the place"""

    try:
        time = message.text
        if ':' in time:
            event_data.time = time
        elif '-' in time:
            hours, minutes = time.split("-")
            event_data.time = f"{hours}:{minutes}"
        elif ' ' in time:
            hours, minutes = time.split(" ")
            event_data.time = f"{hours}:{minutes}"

        if db_event.event_datetime_exists(event_data.date, time):
            print("Time exists")
            msg_data = bot.send_message(message.chat.id, ev_d.event_time_exists_text)
            bot.register_next_step_handler(msg_data, add_time_for_event)
            return

        if event_data.event_id == 1:
            msg = f"{ev_d.set_event_name_text}{ev_d.events_to_add_text_tuple[event_data.event_id]}:"
            msg_data = bot.send_message(message.chat.id, msg)
            bot.register_next_step_handler(msg_data, set_name_for_event)
        else:
            bot.send_message(message.chat.id, ev_d.choose_event_location_text, reply_markup=choose_location_markup)

    except ValueError:
        msg_data = bot.send_message(message.chat.id, ev_d.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)

    except Exception as e:
        print(f"ОШИБОЧКА В add_time_for_event: {e}")
        msg_data = bot.send_message(message.chat.id, ev_d.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)


def set_name_for_event(message: Message):
    """Get event name from the input and ask to set the place"""
    event_data.event_name = message.text
    bot.send_message(message.chat.id, ev_d.choose_event_location_text, reply_markup=choose_location_markup)


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter(type="url"))
def add_new_location(call: CallbackQuery):
    """Ask to input the URL for a new location"""
    msg_data = bot.send_message(call.message.chat.id, ev_d.enter_location_url_text)
    bot.register_next_step_handler(msg_data, save_location_url)


def save_location_url(message: Message):
    """Save URL for a new location. Ask a name for the Location."""

    text = message.text.split("\n")
    for url in text:
        if "http" in url:
            if db_event.location_url_exists(url):
                bot.send_message(message.chat.id, ev_d.location_url_exists_text, reply_markup=choose_location_markup)
            else:
                location_data.url = url
                msg_data = bot.send_message(message.chat.id, ev_d.enter_location_name_text)
                bot.register_next_step_handler(msg_data, save_new_location_and_event)
        else:
            msg_data = bot.send_message(message.chat.id, ev_d.wrong_location_url_text)
            bot.register_next_step_handler(msg_data, save_location_url)


def save_new_location_and_event(message: Message):
    """Save new location and event"""

    if db_event.location_name_exists(message.text):
        msg_data = bot.send_message(message.chat.id, ev_d.location_name_exists_text)
        bot.register_next_step_handler(msg_data, save_new_location_and_event)
        return
    else:
        location_id = db_event.add_location(message.text, location_data.url)
        bot.send_message(message.chat.id, f"{ev_d.new_location_text}{message.text}")

    if event_data.is_in_progress:
        location_data.location_name = message.text
        event_data.eid = db_event.add_event(event_data.event_id, event_data.event_name,
                                            event_data.date, event_data.time, location_id)
        bot.send_message(message.chat.id, f"{ev_d.new_location_text}{location_data.location_name}")
        print(f"save_new_location_and_event {event_data.event_id},"
              f"{event_data.event_name}, {event_data.date, event_data.time}")
        if event_data.event_id == 2:
            msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.add_concert_songs_text}"
            bot.send_message(message.chat.id, msg, reply_markup=add_concert_songs_buttons(event_data.eid))

        else:
            msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.want_repeat_text}"
            bot.send_message(message.chat.id, msg, reply_markup=repeat_buttons(event_data.eid))

        db_attendance.create_new_attendance(event_data.eid)
        bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=None)
        event_data.is_in_progress = False


@bot.callback_query_handler(func=None, calendar_config=repeat_callback.filter())
def show_repeat_period_buttons(call: CallbackQuery):
    """Show buttons to choose repeat interval"""

    print(f"show_repeat_event_buttons {call.data}")
    _, eid = call.data.split(":")
    call_config = "interval"
    data = []
    for i, interval in enumerate(ev_d.event_repeat_text_tuple):
        data.append((interval, f"{call_config}:{eid}:{i}"))

    bot.send_message(call.message.chat.id, ev_d.choose_period_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=interval_callback.filter())
def number_of_repeats(call: CallbackQuery):
    """Ask to enter the number"""

    print(f"number_of_repeats {call.data}")
    _, e_id, interval = call.data.split(":")
    # Save data to use in the next function set_event_repeating
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    msg_data = bot.send_message(call.message.chat.id, ev_d.set_repeat_times_text)
    bot.register_next_step_handler(msg_data, check_data_for_event_repeating, e_id, interval)


def check_data_for_event_repeating(message: Message, e_id, interval):
    """Repeat event № times with defined interval"""

    amount = message.text

    if not amount.isdigit():
        msg_data = bot.send_message(message.chat.id, ev_d.digits_ERROR_text)
        bot.register_next_step_handler(msg_data, check_data_for_event_repeating, e_id, interval)

    _, event_id, event_name, event_date, event_time, location_id, comment = db_event.get_event_by_id(e_id)
    new_date = datetime.strptime(event_date, "%Y-%m-%d")

    count = amount
    for i in range(int(amount)):

        new_date += timedelta(weeks=(1 * (int(interval) + 1)))
        new_date = new_date.strftime("%Y %m %d")
        print(f"set_event_repeating {new_date}")

        if db_event.event_datetime_exists(new_date, event_time):
            year, month, day = new_date.split(" ")
            msg_date = f"{int(day)} {ev_d.chosen_months_text_tuple[int(month)-1]} {year} года в {event_time}"
            bot.send_message(message.chat.id, f"{ev_d.datetime_event_exists_text} "
                                              f"{msg_date}\n{ev_d.repeat_event_skipped_text}")
            count -= 1
            continue

        eid = db_event.add_event(event_id, event_name, new_date, event_time, location_id)
        db_attendance.create_new_attendance(eid)

    bot.send_message(message.chat.id, f"Создано {count} повторных событий.")


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter(type="db"))
def choose_location(call: CallbackQuery):
    """Show the location buttons"""

    locations = db_event.get_all_locations()
    call_data, _ = call.data.split(":")
    data = []
    for location_id, location_name, url in locations:
        data.append((location_name, f"{call_data}:{location_id}"))
    bot.send_message(call.message.chat.id, ev_d.choose_location_text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter())
def save_event(call: CallbackQuery):
    """Get location from the callback data and save the event"""

    _, location_id = call.data.split(":")
    event_data.eid = db_event.add_event(event_data.event_id, event_data.event_name,
                                        event_data.date, event_data.time, location_id)
    if event_data.event_id == 2:
        msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.add_concert_songs_text}"
        bot.send_message(call.message.chat.id, msg, reply_markup=add_concert_songs_buttons(event_data.eid))

    else:
        msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.want_repeat_text}"
        bot.send_message(call.message.chat.id, msg, reply_markup=repeat_buttons(event_data.eid))
    db_attendance.create_new_attendance(event_data.eid)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    event_data.is_in_progress = False


@bot.callback_query_handler(func=None, calendar_config=show_attendance_callback.filter())
def event_attendance(call: CallbackQuery):
    """Display singers attendance for an event"""

    _, _id = call.data.split(":")
    print(f"event_attendance {call.data}")
    icons = ("OK", "NOTOK", "WHAT?")
    attendance_data = [
        (fullname, telegram_name, icons[int(attendance)])
        for fullname, telegram_name, attendance in db_attendance.get_attendance_by_event_id(int(_id))
    ]
    bot.send_message(call.message.chat.id, "Отметки присутствия", reply_markup=message_buttons(attendance_data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery):
    """Create calendar day buttons"""
    _, event_id, year, month = call.data.split(":")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_days(int(year), int(month), int(event_id)))


@bot.callback_query_handler(func=None, calendar_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery):
    """Create calendar month buttons"""
    _, event_id, year = call.data.split(":")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_months(int(year), int(event_id)))


@bot.callback_query_handler(func=lambda call: call.data == EMTPY_FIELD)
def callback_empty_field_handler(call: CallbackQuery):
    """Do nothing for the empty buttons"""
    return
