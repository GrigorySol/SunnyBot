from datetime import datetime, date, timedelta
import inspect

from config import VIP
from loader import bot, log
from database_control import db_event, db_attendance, db_singer
from telebot.types import Message, CallbackQuery
from misc.edit_functions import enter_new_event_time
from misc import dicts, keys, callback_dict as cd


class EventData:
    def __init__(self):
        self.event_id = None
        self.event_type = None      # 0 - None, 1 - Мероприятие, 2 - Концерт, 3 - Репетиция
        self.event_name = None
        self.date = None
        self.time = None
        self.is_in_progress = False


event_data = EventData()


@bot.message_handler(commands=['calendar'])
def calendar_command(message: Message):
    """Show calendar buttons"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    now = date.today()
    event_id = "0"
    bot.send_message(
        message.chat.id,
        dicts.events.set_event_date_text,
        reply_markup=keys.calendar.generate_calendar_days(
            message.from_user.id, now.year, now.month, int(event_id)
        )
    )


@bot.callback_query_handler(func=None, calendar_config=keys.call.calendar_data.filter(event_type="0"))
def calendar_show_event(call: CallbackQuery):
    """Show events for the chosen date"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    *_, year, month, day = call.data.split(":")
    # Show all events for this day
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    events = db_event.search_event_by_date(event_data.date)
    call_config = cd.event_display_text
    data = []

    if not events:
        bot.send_message(call.message.chat.id, dicts.events.no_event_text)
        return

    singer_id = db_singer.get_singer_id(call.from_user.id)
    for event_id, _, event_name, event_time in events:
        participant = db_attendance.get_singer_attendance_for_event(event_id, singer_id)
        if participant or db_singer.is_admin(call.from_user.id):
            data.append({"text": f"{event_name} {event_time}", "callback_data": f"{call_config}:{event_id}"})

    if data:
        msg = f"{dicts.events.current_events_text} {day} " \
               f"{dicts.events.chosen_months_text_tuple[int(month) - 1]} {year} года:"
    else:
        msg = dicts.events.no_participation_text
        bot.send_message(VIP, f"@{call.from_user.username} {call.from_user.first_name}\n"
                              f"{year} {month} {day}")

    markup = keys.buttons.buttons_markup(data)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.calendar_data.filter(event_type="4"))
def edit_event_date(call: CallbackQuery):
    """Edit date for the chosen event"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_type, event_id, year, month, day = call.data.split(":")
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    # Edit event date
    msg = bot.send_message(call.message.chat.id,
                           f"{dicts.events.to_add_text_tuple[int(event_type)]} на {day} "
                           f"{dicts.events.chosen_months_text_tuple[int(month) - 1]} {year} года.\n"
                           f"{dicts.events.set_event_time_text}")
    bot.register_next_step_handler(msg, enter_new_event_time, int(event_id), event_data.date)
    # bot.delete_message(call.message.chat.id, call.message.id)   # TODO: display event info


@bot.callback_query_handler(func=None, calendar_config=keys.call.calendar_data.filter())
def add_event_time(call: CallbackQuery):
    """Add time for a new event"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_type, _, year, month, day = call.data.split(":")
    event_data.date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    # Continue to add an event
    event_data.is_in_progress = True
    event_data.event_type = int(event_type)
    event_data.event_name = dicts.events.to_save_text_tuple[event_data.event_type]
    msg = f"{event_data.event_name} на {day} " \
          f"{dicts.events.chosen_months_text_tuple[int(month) - 1]} {year} года.\n{dicts.events.set_event_time_text}"
    msg_data = bot.send_message(call.message.chat.id, msg)
    bot.register_next_step_handler(msg_data, add_time_for_event)
    # bot.delete_message(call.message.chat.id, call.message.id)   # TODO: display event info


def add_time_for_event(message: Message):
    """Get time from the input and ask to name the event or set the place"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    time = message.text
    if message.text and "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if ':' in time:
        event_data.time = time
    elif '-' in time:
        hours, minutes = time.split("-")
        event_data.time = f"{hours}:{minutes}"
    elif ' ' in time:
        hours, minutes = time.split(" ")
        event_data.time = f"{hours}:{minutes}"
    else:
        msg_data = bot.send_message(message.chat.id, dicts.events.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)
        return

    if db_event.event_datetime_exists(event_data.date, event_data.time):
        msg_data = bot.send_message(message.chat.id, dicts.events.event_time_exists_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)
        return

    if event_data.event_type == 1:
        msg = f"{dicts.events.set_event_name_text}{dicts.events.to_add_text_tuple[event_data.event_type]}:"
        msg_data = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_data, set_name_for_event)
    else:
        bot.send_message(
            message.chat.id,
            dicts.events.choose_event_location_text,
            reply_markup=keys.buttons.choose_location_buttons(event_data.event_id)
        )


def set_name_for_event(message: Message):
    """Get event name from the input and ask to set the place"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    if message.text and "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    event_data.event_name = f"💃 {message.text}"
    bot.send_message(
        message.chat.id,
        dicts.events.choose_event_location_text,
        reply_markup=keys.buttons.choose_location_buttons(event_data.event_id)
    )


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_event_location_callback.filter(type="url"))
def add_new_location(call: CallbackQuery):
    """Ask to input the URL for a new location"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    event_data.event_id = event_id
    msg_data = bot.send_message(call.message.chat.id, dicts.events.enter_location_url_text)
    bot.register_next_step_handler(msg_data, check_location_url, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def check_location_url(message: Message, event_id=None):
    """Check if URL for the location exists. Ask a name for the Location."""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    if not message.text or "отмена" in message.text.lower():
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if "https://" in message.text:
        if db_event.location_url_exists(message.text):
            bot.send_message(
                message.chat.id,
                dicts.events.location_url_exists_text,
                reply_markup=keys.buttons.choose_location_buttons(event_data.event_id)
            )
        else:
            msg_data = bot.send_message(message.chat.id, dicts.events.enter_location_name_text)
            bot.register_next_step_handler(msg_data, save_location_and_event, message.text, event_id)
    else:
        msg_data = bot.send_message(message.chat.id, dicts.events.wrong_location_url_text)
        bot.register_next_step_handler(msg_data, check_location_url, event_id)


def save_location_and_event(message: Message, url, event_id):
    """Save location and event"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if db_event.location_name_exists(message.text):
        msg_data = bot.send_message(message.chat.id, dicts.events.location_name_exists_text)
        bot.register_next_step_handler(msg_data, save_location_and_event, url, event_id)
        return
    else:
        location_id = db_event.add_location(message.text, url)
        bot.send_message(message.chat.id, f"{dicts.events.new_location_text}{message.text}")

    if event_data.is_in_progress:
        save_new_event(location_id, message)
    elif event_id:
        msg = dicts.changes.location_changed_text
        db_event.edit_event_location(event_id, location_id)
        bot.send_message(message.chat.id, msg)


def save_new_event(location_id, message):
    """Save new event and display buttons depending on event type."""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    event_data.event_id = db_event.add_event(event_data.event_type, event_data.event_name,
                                             event_data.date, event_data.time, location_id)
    print(f"{event_data.event_type}, "
          f"{event_data.event_name}, {event_data.date, event_data.time}")

    msg = f"{dicts.events.new_event_text}{event_data.event_name}"
    bot.send_message(message.chat.id, msg)

    db_attendance.add_all_singers_attendance(event_data.event_id)
    event_data.is_in_progress = False


@bot.callback_query_handler(func=None, calendar_config=keys.call.repeat_callback.filter())
def show_repeat_interval_buttons(call: CallbackQuery):
    """Show buttons to choose interval"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    call_config = cd.event_interval_text
    data = []
    for i, text in enumerate(dicts.events.event_repeat_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{event_id}:{i}"})

    msg = dicts.events.choose_period_text
    markup = keys.buttons.buttons_markup(data, event_id=event_id, menu_btn=True)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.interval_callback.filter())
def number_of_repeats(call: CallbackQuery):
    """Ask to enter the number"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_id, interval = call.data.split(":")
    # Save data to use in the next function set_event_repeating
    msg_data = bot.send_message(call.message.chat.id, dicts.events.set_repeat_times_text)
    bot.register_next_step_handler(msg_data, check_data_for_event_repeating, event_id, interval)
    bot.delete_message(call.message.chat.id, call.message.id)


def check_data_for_event_repeating(message: Message, event_id, interval):
    """Repeat event № times with defined interval"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {message.text}\t\t {message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    amount = message.text

    if not amount.isdigit():
        msg_data = bot.send_message(message.chat.id, dicts.events.digits_ERROR_text)
        bot.register_next_step_handler(msg_data, check_data_for_event_repeating, event_id, interval)

    _, event_type, event_name, event_date, event_time, location_id, comment = db_event.get_event_by_id(event_id)
    new_date = datetime.strptime(event_date, "%Y-%m-%d")

    for i in range(int(amount)):

        new_date += timedelta(weeks=(1 * (int(interval) + 1)))
        if db_event.event_datetime_exists(new_date.date(), event_time):
            year, month, day = new_date.strftime("%Y %m %d").split(" ")
            msg_date = f"{int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]} {year} года в {event_time}"
            bot.send_message(message.chat.id, f"{dicts.events.datetime_event_exists_text}\n"
                                              f"{msg_date}\n{dicts.events.repeat_event_skipped_text}")
            continue

        new_event_id = db_event.add_event(event_type, event_name, new_date.date(), event_time, location_id)
        db_attendance.add_all_singers_attendance(new_event_id)

    bot.send_message(message.chat.id, dicts.events.event_repeated_text)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_event_location_callback.filter(type="db"))
def choose_location(call: CallbackQuery):
    """Show the location buttons"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    locations = db_event.get_all_locations()
    call_data, _, event_id = call.data.split(":")
    event_data.event_id = event_id
    data = []
    for location_id, text, url in locations:
        data.append({"text": text, "callback_data": f"{call_data}:{location_id}:{event_id}"})

    msg = dicts.events.choose_location_text
    markup = keys.buttons.buttons_markup(data)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_event_location_callback.filter())
def save_event(call: CallbackQuery):
    """Get location from the callback data and save the event"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, location_id, _ = call.data.split(":")
    if event_data.is_in_progress:
        save_new_event(location_id, call.message)
        bot.delete_message(call.message.chat.id, call.message.id)
    else:
        msg = dicts.changes.location_changed_text
        db_event.edit_event_location(event_data.event_id, location_id)
        bot.send_message(call.message.chat.id, msg)

    call_config = cd.selected_text
    event = db_event.get_event_by_id(event_data.event_id)

    if event[1] == 2:
        options = dicts.changes.edit_concert_text_tuple
    else:
        options = dicts.changes.edit_event_text_tuple

    from handlers.admin.admin_changes import create_option_buttons
    create_option_buttons(call.message, call_config, event_data.event_id, options)


@bot.callback_query_handler(func=None, calendar_config=keys.call.calendar_factory.filter())
def calendar_action_handler(call: CallbackQuery):
    """Create calendar day buttons"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_type, event_id, year, month = call.data.split(":")
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=keys.calendar.generate_calendar_days(
            call.from_user.id, int(year), int(month), int(event_type), event_id
        )
    )


@bot.callback_query_handler(func=None, calendar_config=keys.call.calendar_zoom.filter())
def calendar_zoom_out_handler(call: CallbackQuery):
    """Create calendar month buttons"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_type, event_id, year = call.data.split(":")
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=keys.calendar.generate_calendar_months(
            int(year), int(event_type), event_id)
    )


@bot.callback_query_handler(func=lambda call: call.data == keys.calendar.EMTPY_FIELD)
def callback_empty_field_handler(call: CallbackQuery):
    """Do nothing for the empty buttons"""
    return
