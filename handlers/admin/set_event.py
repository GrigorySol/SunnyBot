from datetime import datetime, date
from loader import bot
from database_control import db_event
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import calendar_zoom, calendar_factory, \
    calendar_data, location_callback, repeat_callback, period_callback
from keyboards.inline.calendar_buttons import generate_calendar_days, generate_calendar_months, EMTPY_FIELD
from keyboards.inline.choice_buttons import chose_location_markup, callback_buttons, repeat_buttons
from misc.messages.singer_dictionary import NOTHING
from misc.messages.event_dictionary import *


class EventData:
    def __init__(self):
        self.event_id = None
        self.event_name = "Репетиция"
        self.date = None
        self.datetime = None
        self.is_in_progress = False
        self.eid = None
        self.period = None


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
    bot.send_message(message.chat.id, set_event_date_text,
                     reply_markup=generate_calendar_days(now.year, now.month, int(event_id)))


@bot.callback_query_handler(func=None, calendar_config=calendar_data.filter())
def calendar_datetime_handler(call: CallbackQuery):
    """Show events if the event_id is 0 or continue to add an event"""

    _, event_id, year, month, day = call.data.split(":")
    if event_id == "0":
        # Show all events for this day
        received_date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}%"
        events = db_event.search_event_by_date(received_date)
        call_config = "event"
        data = []

        if not events:
            bot.send_message(call.message.chat.id, no_event_text)
            return
        for event in events:
            event_time = event[3].split(" ")[1][0:5]
            data.append((f"{event[2]} {event_time}", f"{call_config}:{event[0]}"))

        text = f"{current_events_text} {day} {chosen_months_text_tuple[int(month) - 1]} {year} года:"
        bot.send_message(call.message.chat.id, text, reply_markup=callback_buttons(data))

    else:
        # Continue to add an event
        event_data.is_in_progress = True
        event_data.event_id = int(event_id)
        event_data.event_name = events_to_add_text_tuple[event_data.event_id]
        event_data.date = (int(year), int(month), int(day))
        msg = f"Вы выбрали {events_to_add_text_tuple[event_data.event_id]} на {day} " \
              f"{chosen_months_text_tuple[int(month) - 1]} {year} года.\n{set_event_time_text}"
        msg_data = bot.send_message(call.message.chat.id, msg)
        bot.register_next_step_handler(msg_data, add_time_for_event)


def add_time_for_event(message: Message):
    """Get time from the input and ask to name the event or set the place"""

    try:
        time = message.text
        if ':' in time:
            hours, minutes = time.split(":")
        elif '-' in time:
            hours, minutes = time.split("-")
        else:
            hours, minutes = time.split(" ")
        event_data.datetime = datetime(event_data.date[0], event_data.date[1], event_data.date[2],
                                       int(hours), int(minutes))

        if db_event.search_event_by_date(event_data.datetime):
            print("Time exists")
            msg_data = bot.send_message(message.chat.id, event_time_exists_text)
            bot.register_next_step_handler(msg_data, add_time_for_event)
            return

        if event_data.event_id == 1:
            msg_data = bot.send_message(message.chat.id,
                                        f"{set_event_name_text}{events_to_add_text_tuple[event_data.event_id]}:")
            bot.register_next_step_handler(msg_data, set_name_for_event)
        else:
            bot.send_message(message.chat.id, chose_event_location_text, reply_markup=chose_location_markup)

    except ValueError:
        msg_data = bot.send_message(message.chat.id, wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)

    except Exception as e:
        print(f"ОШИБОЧКА В add_time_for_event: {e}")
        msg_data = bot.send_message(message.chat.id, wrong_event_time_text)
        bot.register_next_step_handler(msg_data, add_time_for_event)


def set_name_for_event(message: Message):
    """Get event name from the input and ask to set the place"""
    event_data.event_name = message.text
    bot.send_message(message.chat.id, chose_event_location_text, reply_markup=chose_location_markup)


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter(type="url"))
def add_new_location(call: CallbackQuery):
    """Ask to input the URL for a new location"""
    msg_data = bot.send_message(call.message.chat.id, enter_location_url_text)
    bot.register_next_step_handler(msg_data, save_location_url)


def save_location_url(message: Message):
    """Save URL for a new location. Ask a name for the Location."""
    text = message.text.split("\n")
    for url in text:
        if "http" in url:
            if db_event.location_url_exists(url):
                bot.send_message(message.chat.id, location_url_exists, reply_markup=chose_location_markup)
            else:
                location_data.url = url
                msg_data = bot.send_message(message.chat.id, enter_location_name_text)
                bot.register_next_step_handler(msg_data, save_new_location_and_event)
        else:
            msg_data = bot.send_message(message.chat.id, wrong_location_url_text)
            bot.register_next_step_handler(msg_data, save_location_url)


def save_new_location_and_event(message: Message):
    """Save new location and event"""

    if db_event.location_name_exists(message.text):
        msg_data = bot.send_message(message.chat.id, location_name_exists_text)
        bot.register_next_step_handler(msg_data, save_new_location_and_event)
    else:
        location_data.location_name = message.text
        location_id = db_event.add_location(message.text, location_data.url)
        event_data.eid = db_event.add_event(event_data.event_id, event_data.event_name,
                                            event_data.datetime, location_id)
        bot.send_message(message.chat.id, f"{new_location_text}{location_data.location_name}")
        msg = f"{new_event_text}{event_data.event_name}\n{want_repeat_text}"
        print(f"save_new_location_and_event {event_data.event_id}, {event_data.event_name}, {event_data.datetime}")
        bot.send_message(message.chat.id, msg, reply_markup=repeat_buttons(event_data.eid))
        bot.edit_message_reply_markup(message.chat.id, message.id, reply_markup=None)
        event_data.is_in_progress = False


@bot.callback_query_handler(func=None, calendar_config=repeat_callback.filter())
def show_repeat_period_buttons(call: CallbackQuery):
    """Show buttons to chose repeat period"""

    print(f"show_repeat_event_buttons {call.data}")
    _, eid = call.data.split(":")
    call_config = "period"
    data = []
    for i, period in enumerate(event_repeat_text_tuple):
        data.append((period, f"{call_config}:{eid}:{i}"))

    bot.send_message(call.message.chat.id, chose_period_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=period_callback.filter())
def number_of_repeats(call: CallbackQuery):
    """Ask to enter the number"""

    print(f"number_of_repeats {call.data}")
    _, eid, period = call.data.split(":")
    # Save data to use in the next function set_event_repeating
    event_data.eid = eid
    event_data.period = period
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    msg_data = bot.send_message(call.message.chat.id, set_repeat_times_text)
    bot.register_next_step_handler(msg_data, set_event_repeating)


def set_event_repeating(message: Message):
    """Repeat event № times with defined period"""

    # TODO: Create routing to apply № of repeats of event every 'period'
    print(message.text)     # repeating times
    print(f"Use THIS {event_data.eid}, {event_data.period}")
    bot.send_message(message.chat.id, NOTHING)


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter(type="db"))
def chose_location(call: CallbackQuery):
    """Show the location buttons"""

    locations = db_event.get_all_locations()
    call_data, _ = call.data.split(":")
    data = []
    for location_id, location_name, url in locations:
        data.append((location_name, f"{call_data}:{location_id}"))
    bot.send_message(call.message.chat.id, chose_location_text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=location_callback.filter())
def save_event(call: CallbackQuery):
    """Get location from the callback data and save the event"""

    _, location_id = call.data.split(":")
    event_data.eid = db_event.add_event(event_data.event_id, event_data.event_name,
                                        event_data.datetime, location_id)

    msg = f"{new_event_text}{event_data.event_name}\n{want_repeat_text}"
    bot.send_message(call.message.chat.id, msg, reply_markup=repeat_buttons(event_data.eid))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    event_data.is_in_progress = False


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
    bot.answer_callback_query(call.id)
