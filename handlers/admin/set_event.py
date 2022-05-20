from datetime import datetime, date, timedelta
from loader import bot
from database_control import db_event, db_attendance, db_singer
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import calendar_zoom, calendar_factory, \
    calendar_data, location_callback, repeat_callback, interval_callback, show_participation_callback, \
    remove_participation_callback, singer_attendance_callback

from keyboards.inline.calendar_buttons import generate_calendar_days, generate_calendar_months, EMTPY_FIELD

from keyboards.inline.choice_buttons import choose_location_markup, callback_buttons, \
    repeat_buttons, add_concert_songs_buttons, message_buttons, show_participation, close_btn
from misc.edit_functions import enter_new_event_time
from misc.messages import event_dictionary as ev_d, attendance_dictionary as at_d


class EventData:
    def __init__(self):
        self.event_id = None
        self.event_type = None      # 0 - None, 1 - Мероприятие, 2 - Концерт, 3 - Репетиция
        self.event_name = "Репетиция"
        self.date = None
        self.time = None
        self.is_in_progress = False


event_data = EventData()


@bot.message_handler(commands=['calendar'])
def calendar_command_handler(message: Message):
    """Show calendar buttons"""
    now = date.today()
    event_id = "0"
    bot.send_message(message.chat.id, ev_d.set_event_date_text,
                     reply_markup=generate_calendar_days(now.year, now.month, int(event_id)))


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter(event_type="0"))
def calendar_show_event_handler(call: CallbackQuery):
    """Show events for the chosen day."""

    *_, year, month, day = call.data.split(":")
    # Show all events for this day
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    events = db_event.search_event_by_date(event_data.date)
    call_config = "event"
    data = []

    if not events:
        bot.send_message(call.message.chat.id, ev_d.no_event_text)
        return
    for event_id, _, event_name, event_time in events:
        data.append((f"{event_name} {event_time}", f"{call_config}:{event_id}"))

    text = f"{ev_d.current_events_text} {day} {ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года:"
    bot.send_message(call.message.chat.id, text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter(event_type="4"))
def edit_event_date_handler(call: CallbackQuery):
    """Edit date for the chosen event"""

    _, event_type, event_id, year, month, day = call.data.split(":")
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    # Edit event date
    msg = bot.send_message(call.message.chat.id,
                           f"Вы выбрали {ev_d.events_to_add_text_tuple[int(event_type)]} на {day} "
                           f"{ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года.\n{ev_d.set_event_time_text}")
    bot.register_next_step_handler(msg, enter_new_event_time, int(event_id), event_data.date)


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter())
def add_event_time_handler(call: CallbackQuery):
    """Add time for a new event"""

    _, event_type, _, year, month, day = call.data.split(":")
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    # Continue to add an event
    event_data.is_in_progress = True
    event_data.event_type = int(event_type)
    event_data.event_name = ev_d.events_to_save_text_tuple[event_data.event_type]
    msg = f"Вы выбрали {ev_d.events_to_add_text_tuple[event_data.event_type]} на {day} " \
          f"{ev_d.chosen_months_text_tuple[int(month) - 1]} {year} года.\n{ev_d.set_event_time_text}"
    msg_data = bot.send_message(call.message.chat.id, msg)
    bot.register_next_step_handler(msg_data, add_time_for_event)


def add_time_for_event(message: Message):
    """Get time from the input and ask to name the event or set the place"""

    time = message.text
    if ':' in time:
        event_data.time = time
    elif '-' in time:
        hours, minutes = time.split("-")
        event_data.time = f"{hours}:{minutes}"
    elif ' ' in time:
        hours, minutes = time.split(" ")
        event_data.time = f"{hours}:{minutes}"
    else:
        msg_data = bot.send_message(message.chat.id, ev_d.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)

    if db_event.event_datetime_exists(event_data.date, time):
        msg_data = bot.send_message(message.chat.id, ev_d.event_time_exists_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)
        return

    if event_data.event_type == 1:
        msg = f"{ev_d.set_event_name_text}{ev_d.events_to_add_text_tuple[event_data.event_type]}:"
        msg_data = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_data, set_name_for_event)
    else:
        bot.send_message(message.chat.id, ev_d.choose_event_location_text, reply_markup=choose_location_markup)


def set_name_for_event(message: Message):
    """Get event name from the input and ask to set the place"""
    event_data.event_name = message.text
    bot.send_message(message.chat.id, ev_d.choose_event_location_text, reply_markup=choose_location_markup)


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter(type="url"))
def add_new_location(call: CallbackQuery):
    """Ask to input the URL for a new location"""
    msg_data = bot.send_message(call.message.chat.id, ev_d.enter_location_url_text)
    bot.register_next_step_handler(msg_data, check_location_url)


def check_location_url(message: Message):
    """Check if URL for the location exists. Ask a name for the Location."""

    text = message.text.split("\n")
    for url in text:
        if "http" in url:
            if db_event.location_url_exists(url):
                bot.send_message(message.chat.id, ev_d.location_url_exists_text, reply_markup=choose_location_markup)
            else:
                msg_data = bot.send_message(message.chat.id, ev_d.enter_location_name_text)
                bot.register_next_step_handler(msg_data, save_location_and_event, url)
        else:
            msg_data = bot.send_message(message.chat.id, ev_d.wrong_location_url_text)
            bot.register_next_step_handler(msg_data, check_location_url)


def save_location_and_event(message: Message, url):
    """Save location and event"""

    if db_event.location_name_exists(message.text):
        msg_data = bot.send_message(message.chat.id, ev_d.location_name_exists_text)
        bot.register_next_step_handler(msg_data, save_location_and_event, url)
        return
    else:
        location_id = db_event.add_location(message.text, url)
        bot.send_message(message.chat.id, f"{ev_d.new_location_text}{message.text}")

    if event_data.is_in_progress:
        save_new_event(location_id, message)


def save_new_event(location_id, message):
    """Save new event and display buttons depending on event type."""
    event_data.event_id = db_event.add_event(event_data.event_type, event_data.event_name,
                                             event_data.date, event_data.time, location_id)
    print(f"save_new_event {event_data.event_type},"
          f"{event_data.event_name}, {event_data.date, event_data.time}")
    if event_data.event_type == 2:
        msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.add_concert_songs_text}"
        markup = show_participation(event_data.event_id)
        for buttons in add_concert_songs_buttons(event_data.event_id).keyboard:
            markup.add(*buttons)
        bot.send_message(message.chat.id, msg, reply_markup=markup)

    elif event_data.event_type == 3:
        msg = f"{ev_d.new_event_text}{event_data.event_name}\n{ev_d.want_repeat_text}"
        markup = show_participation(event_data.event_id)

        for buttons in repeat_buttons(event_data.event_id).keyboard:
            markup.add(*buttons)
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    else:
        markup = show_participation(event_data.event_id)
        markup.add(close_btn)
        msg = f"{ev_d.new_event_text}{event_data.event_name}"
        bot.send_message(message.chat.id, msg, reply_markup=markup)

    # TODO: Add singers attendance edit
    db_attendance.create_new_attendance(event_data.event_id)
    bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=None)
    event_data.is_in_progress = False


@bot.callback_query_handler(func=None, calendar_config=repeat_callback.filter())
def show_repeat_interval_buttons(call: CallbackQuery):
    """Show buttons to choose interval"""

    print(f"show_repeat_event_buttons {call.data}")
    _, event_id = call.data.split(":")
    call_config = "interval"
    data = []
    for i, interval in enumerate(ev_d.event_repeat_text_tuple):
        data.append((interval, f"{call_config}:{event_id}:{i}"))

    bot.send_message(call.message.chat.id, ev_d.choose_period_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=interval_callback.filter())
def number_of_repeats(call: CallbackQuery):
    """Ask to enter the number"""

    print(f"number_of_repeats {call.data}")
    _, event_id, interval = call.data.split(":")
    # Save data to use in the next function set_event_repeating
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    msg_data = bot.send_message(call.message.chat.id, ev_d.set_repeat_times_text)
    bot.register_next_step_handler(msg_data, check_data_for_event_repeating, event_id, interval)


def check_data_for_event_repeating(message: Message, event_id, interval):
    """Repeat event № times with defined interval"""

    amount = message.text

    if not amount.isdigit():
        msg_data = bot.send_message(message.chat.id, ev_d.digits_ERROR_text)
        bot.register_next_step_handler(msg_data, check_data_for_event_repeating, event_id, interval)

    _, event_id, event_name, event_date, event_time, location_id, comment = db_event.get_event_by_id(event_id)
    new_date = datetime.strptime(event_date, "%Y-%m-%d")

    for i in range(int(amount)):

        new_date += timedelta(weeks=(1 * (int(interval) + 1)))
        if db_event.event_datetime_exists(new_date.date(), event_time):
            year, month, day = new_date.strftime("%Y %m %d").split(" ")
            msg_date = f"{int(day)} {ev_d.chosen_months_text_tuple[int(month)-1]} {year} года в {event_time}"
            bot.send_message(message.chat.id, f"{ev_d.datetime_event_exists_text}\n"
                                              f"{msg_date}\n{ev_d.repeat_event_skipped_text}")
            continue

        eid = db_event.add_event(event_id, event_name, new_date.date(), event_time, location_id)
        db_attendance.create_new_attendance(eid)

    bot.send_message(message.chat.id, f"{ev_d.event_repeated_text}")


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
    print(f"{event_data.event_type}, {event_data.event_name}, {event_data.date}, {event_data.time}, {location_id}")
    save_new_event(location_id, call.message)


@bot.callback_query_handler(func=None, calendar_config=show_participation_callback.filter())
def event_attendance(call: CallbackQuery):
    """Display singers attendance for an event"""

    _, event_id = call.data.split(":")
    print(f"event_attendance {call.data}")
    attendance_data = [
        (fullname, telegram_name, at_d.attendance_pics_tuple[int(attendance)])
        for _, fullname, telegram_name, attendance in db_attendance.get_attendance_by_event_id(int(event_id))
    ]
    bot.edit_message_text(at_d.attendant_singers_text, call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=message_buttons(attendance_data, event_id)
    )


@bot.callback_query_handler(func=None, calendar_config=remove_participation_callback.filter())
def remove_participation(call: CallbackQuery):
    """Display singers to remove from an event"""

    _, event_id = call.data.split(":")
    remove_data = [
        (fullname, f"singer_attendance:remove:{event_id}:{singer_id}")
        for singer_id, fullname, _, _ in db_attendance.get_attendance_by_event_id(int(event_id))
    ]
    bot.edit_message_text(at_d.choose_singer_to_remove_text, call.message.chat.id, call.message.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=callback_buttons(remove_data))


@bot.callback_query_handler(func=None, calendar_config=singer_attendance_callback.filter(action="remove"))
def remove_singer_attendance(call: CallbackQuery):
    """Remove selected singer attendance from an event"""

    *_, event_id, singer_id = call.data.split(":")
    print(f"remove_singer_attendance {call.data}")
    singer_name = db_singer.get_singer_fullname(int(singer_id))

    if not db_attendance.check_singer_attendance_exists(int(event_id), int(singer_id)):
        bot.send_message(call.message.chat.id, f"{singer_name} {at_d.singer_already_removed_text}")
        return

    db_attendance.remove_singer_attendance(int(event_id), int(singer_id))
    bot.send_message(call.message.chat.id, f"{singer_name} {at_d.singer_removed_text}")


@bot.callback_query_handler(func=None, calendar_config=singer_attendance_callback.filter(action="edit"))
def edit_singer_attendance(call: CallbackQuery):
    """Edit singer attendance for an event"""

    *_, event_id, decision = call.data.split(":")
    print(f"edit_singer_attendance {call.data}")
    db_attendance.edit_singer_attendance(int(event_id), call.from_user.id, int(decision))
    bot.send_message(call.message.chat.id, f"{at_d.attendance_changed_text}")


@bot.callback_query_handler(func=None, calendar_config=calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery):
    """Create calendar day buttons"""

    _, event_type, event_id, year, month = call.data.split(":")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_days(int(year), int(month), int(event_type), event_id))


@bot.callback_query_handler(func=None, calendar_config=calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery):
    """Create calendar month buttons"""

    _, event_type, event_id, year = call.data.split(":")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id,
                                  reply_markup=generate_calendar_months(int(year), int(event_type), event_id))


@bot.callback_query_handler(func=lambda call: call.data == EMTPY_FIELD)
def callback_empty_field_handler(call: CallbackQuery):
    """Do nothing for the empty buttons"""
    return
