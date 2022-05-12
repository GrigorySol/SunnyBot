from datetime import datetime, date

from loader import bot
from telebot.types import CallbackQuery, Message
from keyboards.inline.choice_buttons import callback_buttons, choose_location_markup
from keyboards.inline.calendar_buttons import generate_calendar_days
from keyboards.inline import callback_datas as cd
from misc.edit_functions import enter_new_event_time
from misc.messages import event_dictionary as ev_d, singer_dictionary as sin_d, changes_dictionary as ch_d
from database_control import db_songs, db_singer, db_event


@bot.callback_query_handler(func=None, calendar_config=cd.change_callback.filter())
def display_options_to_change(call: CallbackQuery):
    """Display options to change"""

    print(f"We are in display_options_to_change CALL DATA = {call.data}\n")
    _, name, item_id = call.data.split(":")

    if name == "event":  # "Название", "Дату", "Время", "Место", "Комментарий", "УДАЛИТЬ"
        event = db_event.search_event_by_id(int(item_id))

        if not event:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, ev_d.event_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        call_config = "selected_event"
        if event[1] == 2:
            options = ch_d.event_options_to_edit_text_tuple.__add__(("Песни", ))
            print(options)
        else:
            options = ch_d.event_options_to_edit_text_tuple

    else:  # "location" - "Название", "Ссылку на карту", "Ничего", "УДАЛИТЬ
        location = db_event.search_location_by_id(int(item_id))

        if not location:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, ev_d.event_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        call_config = "selected_location"
        options = ch_d.location_options_to_edit_text_tuple

    data = []
    for option_id, option in enumerate(options):
        data.append((option, f"{call_config}:{option_id}:{item_id}"))

    bot.send_message(call.message.chat.id, ch_d.select_option_to_change_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="0"))
def edit_event_name(call: CallbackQuery):
    """Edit name for an Event"""

    print(f"edit_event_name {call.data}")
    _, _, _id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, ch_d.enter_new_event_name_text)
    bot.register_next_step_handler(msg, enter_new_event_name, _id)


def enter_new_event_name(message: Message, event_id):
    """Updates the name for an event"""

    if db_event.edit_event_name(event_id, message.text):
        bot.send_message(message.chat.id, ch_d.event_name_changed_text)

    else:
        bot.send_message(message.chat.id, ch_d.ERROR_text)
        msg = f"ERROR in enter_new_event_name\nData: {message.text} {event_id} "
        bot.send_message(434767263, msg)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="1"))
def edit_event_date(call: CallbackQuery):
    """Edit date for an Event"""

    print(f"edit_event_date {call.data}")
    _, _, _id = call.data.split(":")
    now = date.today()
    event_id = "4"  # edit
    bot.send_message(call.message.chat.id, ev_d.set_event_date_text,
                     reply_markup=generate_calendar_days(now.year, now.month, int(event_id), _id))


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="2"))
def edit_event_time(call: CallbackQuery):
    """Edit time for an Event"""

    print(f"edit_event_time {call.data}")
    _, _, _id = call.data.split(":")
    event_date, _ = db_event.get_event_datetime(_id).split(" ")
    year, month, day = event_date.split("-")
    msg = bot.send_message(call.message.chat.id, ch_d.enter_new_event_time_text)
    bot.register_next_step_handler(msg, enter_new_event_time, _id, year, month, day)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="3"))
def edit_event_location(call: CallbackQuery):
    """Edit location for an Event"""
    print(f"edit_event_location {call.data}")
    bot.send_message(call.message.chat.id, ev_d.choose_event_location_text, reply_markup=choose_location_markup)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="4"))
def edit_comment_event(call: CallbackQuery):
    """Edit comment for an Event"""
    print(f"edit_comment_event {call.data}")
    bot.send_message(call.message.chat.id, sin_d.NOTHING)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="5"))
def delete_event(call: CallbackQuery):
    """DELETE Event"""

    print(f"delete_event {call.data}")
    _, _, _id = call.data.split(":")

    item_name = db_event.search_event_by_id(_id)[2]
    call_config = "delete_confirmation"
    item_type = "event"
    data = []
    msg = f"{ch_d.delete_confirmation_text} {item_name}?"

    for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{_id}:{i}"))

    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=cd.selected_event_callback.filter(option_id="6"))
def edit_event_songs(call: CallbackQuery):
    """Edit songs for a concert"""

    print(f"edit_event_songs {call.data}")
    _, _, _id = call.data.split(":")

    call_config = "change_songs"
    data = []

    for option_id, option_name in enumerate(ch_d.edit_buttons_text_tuple):
        data.append((option_name, f"{call_config}:{_id}:{option_id}"))

    bot.send_message(call.message.chat.id, sin_d.what_to_do_text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=cd.change_songs_callback.filter())
def edit_songs_for_concert(call: CallbackQuery):
    """List of songs to edit"""

    print(f"edit_songs_for_concert {call.data}")
    _, concert_id, option_id = call.data.split(":")

    call_config = "concert_songs"
    data = []

    if option_id == "0":
        option = "add"
        songs = db_songs.get_all_songs()

    else:
        option = "remove"
        songs = db_songs.get_songs_by_event_id(int(concert_id))

    for song_id, song_name, _ in songs:
        data.append((song_name, f"{call_config}:{option}:{concert_id}:{song_id}"))

    bot.send_message(call.message.chat.id, ch_d.edit_buttons_text_tuple, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=cd.concert_songs_callback.filter())
def add_or_remove_songs(call: CallbackQuery):
    """Add or remove songs in concert program"""

    print(f"edit_songs_for_concert {call.data}")
    _, option, concert_id, song_id = call.data.split(":")

    if option == "add":
        if db_event.add_song_to_concert(int(concert_id), int(song_id)):
            song_name = db_songs.get_song_name(int(song_id))
            bot.send_message(call.message.chat.id, f"{ch_d.song_added_to_concert_text} {song_name}")

        else:
            bot.send_message(call.message.chat.id, ch_d.song_already_added)

    else:
        song_name = db_songs.get_song_name(int(song_id))
        db_event.delete_song_from_concert(int(concert_id), int(song_id))
        bot.send_message(call.message.chat.id, f"{ch_d.song_removed_from_concert} {song_name}")


@bot.callback_query_handler(func=None, calendar_config=cd.selected_location_callback.filter(option_id="3"))
def delete_location(call: CallbackQuery):
    """DELETE location"""

    print(f"delete_location {call.data}")
    _, _, _id = call.data.split(":")

    item_name = db_event.search_location_by_id(_id)[2]
    call_config = "delete_confirmation"
    item_type = "location"
    data = []
    msg = f"{ch_d.delete_confirmation_text}\n{item_name}?"

    for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{_id}:{i}"))

    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=cd.delete_confirmation_callback.filter())
def delete_item(call: CallbackQuery):
    """DELETE confirmation"""

    print(f"delete_item {call.data}")
    _, item_type, item_id, action_id = call.data.split(":")
    sticker_id = "CAACAgIAAxkBAAET3TFielLLC-xjt4t8w12Gju8HUNrC-gACpgAD9wLID6sM5POpKsZYJAQ"

    if action_id == "0":
        sticker_id = "CAACAgIAAxkBAAET3TlielLpoQABpzKmmwLZJd46cI8c74QAAh0AA2vtfArV9f-EEVC1CCQE"
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    if item_type == "singer":
        db_singer.delete_singer_by_id(int(item_id))

    elif item_type == "event":
        db_event.delete_event_by_id(int(item_id))

    elif item_type == "location":
        db_event.delete_location_by_id(int(item_id))

    elif item_type == "song":
        db_songs.delete_song_by_id(int(item_id))

    elif item_type == "sheets":
        db_songs.delete_sheets_by_song_id(int(item_id))

    elif item_type == "sounds":
        db_songs.delete_sounds_by_song_id(int(item_id))

    bot.send_message(call.message.chat.id, f"УДАЛЕНО! НАВСЕГДА!!! ХА-ха-ха-ха! ")
    bot.send_sticker(call.message.chat.id, sticker_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
