import datetime
from datetime import date

from config import VIP
from loader import bot
from telebot.types import CallbackQuery, Message, InputMediaPhoto
from misc.edit_functions import enter_new_event_time
from misc import dicts, keys, bot_speech
from database_control import db_songs, db_singer, db_event, db_attendance


@bot.callback_query_handler(func=lambda c: c.data == 'show_suits')
def show_suits(call: CallbackQuery):
    """Display all suits and buttons with suit names"""
    suits = db_singer.get_all_suits()

    if suits:
        call_config = "change"
        item_type = "suit"
        data = []
        suit_data = []

        for suit_id, suit_name, photo in suits:
            data.append((suit_name, f"{call_config}:{item_type}:{suit_id}"))
            suit_data.append(InputMediaPhoto(photo, suit_name))

        bot.send_media_group(call.message.chat.id, suit_data)
        bot.send_message(
            call.message.chat.id, dicts.changes.edit_suit_text, reply_markup=keys.buttons.callback_buttons(data)
        )

    else:
        bot.send_message(call.message.chat.id, dicts.changes.no_suits_to_edit_text)

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="event"))
def display_event_options_to_change(call: CallbackQuery):
    """Display event options to change"""

    print(f"We are in display_event_options_to_change CALL DATA = {call.data}\n")
    _, name, item_id = call.data.split(":")

    # "Название", "Дату", "Время", "Место", "Комментарий", "УДАЛИТЬ"
    event = db_event.search_event_by_id(int(item_id))

    if not event:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.events.event_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    call_config = "selected"
    if event[1] == 2:
        options = dicts.changes.edit_concert_text_tuple
    else:
        options = dicts.changes.edit_event_text_tuple

    create_option_buttons(call.message, call_config, item_id, options)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="location"))
def display_location_options_to_change(call: CallbackQuery):
    """Display location options to change"""

    print(f"We are in display_location_options_to_change CALL DATA = {call.data}\n")
    *_, item_id = call.data.split(":")

    location = db_event.search_location_by_id(int(item_id))

    if not location:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.events.location_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    # "location" - "Название", "Ссылку на карту", "Ничего", "УДАЛИТЬ
    call_config = "selected_location"
    create_option_buttons(call.message, call_config, item_id, dicts.changes.edit_location_text_tuple)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="suit"))
def display_suit_options_to_change(call: CallbackQuery):
    """Display location options to change"""

    print(f"We are in display_suit_options_to_change CALL DATA = {call.data}\n")
    *_, item_id = call.data.split(":")

    suit = db_singer.search_suits_by_id(int(item_id))

    if not suit:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.changes.suit_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    call_config = "selected_suit"
    create_option_buttons(call.message, call_config, item_id, dicts.changes.edit_suit_text_tuple)


def create_option_buttons(message: Message, call_config, item_id, options):
    data = []

    for option_id, option in enumerate(options):
        data.append((option, f"{call_config}:{option_id}:{item_id}"))

    bot.edit_message_text(
        dicts.changes.select_option_to_change_text,
        message.chat.id,
        message.id,
        reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="0"))
def edit_event_name(call: CallbackQuery):
    """Edit name for an Event"""

    print(f"edit_event_name {call.data}")
    *_, event_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_event_name_text)
    bot.register_next_step_handler(msg, enter_new_event_name, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_event_name(message: Message, event_id):
    """Update the name for an event"""

    if message.text and "/" in message.text:
        return

    if db_event.edit_event_name(event_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.name_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {event_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="1"))
def edit_event_date(call: CallbackQuery):
    """Edit date for an Event"""

    print(f"edit_event_date {call.data}")
    *_, event_id = call.data.split(":")
    now = date.today()
    event_type = "4"  # edit
    markup = keys.calendar.generate_calendar_days(now.year, now.month, int(event_type), event_id)
    bot.send_message(call.message.chat.id, dicts.events.set_event_date_text, reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="2"))
def edit_event_time(call: CallbackQuery):
    """Edit time for an Event"""

    print(f"edit_event_time {call.data}")
    *_, event_id = call.data.split(":")
    event_date = db_event.get_event_date(event_id)
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_event_time_text)
    bot.register_next_step_handler(msg, enter_new_event_time, event_id, event_date)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="3"))
def edit_event_location(call: CallbackQuery):
    """Edit location for an Event"""

    print(f"edit_event_location {call.data}")
    bot.send_message(
        call.message.chat.id,
        dicts.events.choose_event_location_text,
        reply_markup=keys.buttons.choose_location_markup
    )
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="4"))
def edit_comment_event(call: CallbackQuery):
    """Edit comment for an Event"""

    print(f"edit_comment_event {call.data}")
    *_, event_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_comment_text)
    bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_event_comment(message: Message, event_id):
    """Update the comment for an event"""

    if message.text and "/" in message.text:
        return

    if db_event.edit_event_comment(event_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.comment_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {event_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="5"))
def edit_event_participant(call: CallbackQuery):
    """Edit Event participants"""

    print(f"edit_event_participant {call.data}")
    *_, event_id = call.data.split(":")
    attendance_data = [
        (fullname, telegram_name, dicts.attends.attendance_pics_tuple[int(attendance)])
        for _, fullname, telegram_name, attendance in db_attendance.get_attendance_by_event_id(event_id)
    ]
    bot.edit_message_text(
        dicts.attends.attendant_singers_text,
        call.message.chat.id,
        call.message.id,
        reply_markup=keys.buttons.participant_message_buttons(attendance_data, event_id)
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="6"))
def delete_event(call: CallbackQuery):
    """DELETE Event"""

    print(f"delete_event {call.data}")
    *_, event_id = call.data.split(":")

    item_name = db_event.get_event_name(event_id)
    call_config = "delete_confirmation"
    item_type = "event"
    data = []
    msg = f"{dicts.changes.delete_confirmation_text} {item_name}?"

    for i, answer in enumerate(dicts.changes.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{event_id}:{i}"))

    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=keys.buttons.callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="7"))
def edit_concert_songs(call: CallbackQuery):
    """Edit songs for a concert"""

    print(f"edit_event_songs {call.data}")
    *_, event_id = call.data.split(":")

    call_config = "change_songs"
    data = []

    for option_id, option_name in enumerate(dicts.changes.add_remove_text_tuple):
        data.append((option_name, f"{call_config}:{event_id}:{option_id}"))

    bot.send_message(
        call.message.chat.id, dicts.singers.what_to_do_text, reply_markup=keys.buttons.callback_buttons(data)
    )
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="8"))
def edit_concert_suit(call: CallbackQuery):
    """Show add or remove button to edit suit for a concert"""

    print(f"edit_event_suit {call.data}")
    *_, event_id = call.data.split(":")
    suit = db_event.get_suit_by_event_id(event_id)

    if suit:
        call_config = "remove_suit"
        msg = dicts.changes.concert_suit_change_text
        markup = keys.buttons.callback_buttons([(dicts.changes.suit_change_btn_text, 
                                                 f"{call_config}:{event_id}:{suit[0]}")])
        bot.send_photo(call.message.chat.id, suit[2], reply_markup=keys.buttons.close_markup)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)

    else:
        select_suit_for_concert(call, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def select_suit_for_concert(call, event_id):
    """Display all suits to choose for a concert"""

    suits = db_singer.get_all_suits()
    msg = dicts.changes.choose_suit_text
    call_config = "select_suit"
    data = []
    suit_data = []

    for suit_id, suit_name, photo in suits:
        data.append((suit_name, f"{call_config}:{event_id}:{suit_id}"))
        suit_data.append(InputMediaPhoto(photo, suit_name))

    bot.send_media_group(call.message.chat.id, suit_data)
    bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.remove_suit_callback.filter())
def display_suit_options_to_change(call: CallbackQuery):
    """Remove current concert suit and display suit options to change"""

    print(f"We are in display_suit_options_to_change CALL DATA = {call.data}\n")
    _, event_id, suit_id = call.data.split(":")
    db_event.delete_suit_from_concert(event_id, suit_id)
    select_suit_for_concert(call, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_songs_callback.filter())
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
        songs = db_songs.get_songs_by_event_id(concert_id)

    for song_id, song_name, _ in songs:
        data.append((song_name, f"{call_config}:{option}:{concert_id}:{song_id}"))

    bot.edit_message_text(
        dicts.changes.add_remove_text_tuple[int(option_id)],
        call.message.chat.id,
        call.message.id,
        reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.concert_songs_callback.filter())
def add_or_remove_songs(call: CallbackQuery):
    """Add or remove songs in concert program"""

    print(f"edit_songs_for_concert {call.data}")
    _, option, concert_id, song_id = call.data.split(":")

    if option == "add":
        if db_event.add_song_to_concert(concert_id, song_id):
            song_name = db_songs.get_song_name(song_id)
            bot.send_message(call.message.chat.id, f"{dicts.changes.song_added_to_concert_text} {song_name}")

        else:
            bot.send_message(call.message.chat.id, dicts.changes.song_already_added)

    else:
        song_name = db_songs.get_song_name(song_id)
        db_event.delete_song_from_concert(concert_id, song_id)
        bot.send_message(call.message.chat.id, f"{dicts.changes.song_removed_from_concert} {song_name}")
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.select_suit_callback.filter())
def edit_suit_for_concert(call: CallbackQuery):
    """Add a suit for a concert"""

    print(f"admin_changes.py edit_suit_for_concert {call.data}")
    _, concert_id, suit_id = call.data.split(":")
    if db_event.add_suit_to_concert(concert_id, suit_id):
        bot.edit_message_text(dicts.changes.suit_added_text, call.message.chat.id, call.message.id, reply_markup=None)
    else:
        bot.send_message(call.message.chat.id, dicts.changes.ERROR_text)
        bot.send_message(VIP, f"ERROR in {__name__}\nedit_suit_for_concert {call.data}")


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="0"))
def edit_location_name(call: CallbackQuery):
    """Edit location name"""

    print(f"We are in edit_location_name CALL DATA = {call.data}\n")
    *_, location_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_location_name_text)
    bot.register_next_step_handler(msg, enter_new_location_name, location_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_sticker(
    #     call.message.chat.id,
    #     "CAACAgIAAxkBAAEUN1RiiCW1_TMceKUYF5oulfjmOXpAYgACFgADa-18CgcoBnIvq3DlJAQ"    # Правильный код
    # )


def enter_new_location_name(message: Message, location_id):
    """Update the name for a location"""

    if message.text and "/" in message.text:
        return

    if db_event.edit_location_name(location_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.name_changed_text)

    else:
        bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        msg = f"ERROR in enter_new_suit_name\nData: {message.text} {location_id} "
        bot.send_message(VIP, msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="1"))
def edit_location_url(call: CallbackQuery):
    """Edit location URL"""

    print(f"We are in edit_location_url CALL DATA = {call.data}\n")
    *_, location_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_location_url_text)
    bot.register_next_step_handler(msg, enter_new_location_url, location_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_sticker(
    #     call.message.chat.id,
    #     "CAACAgIAAxkBAAEUN1RiiCW1_TMceKUYF5oulfjmOXpAYgACFgADa-18CgcoBnIvq3DlJAQ"    # Правильный код
    # )


def enter_new_location_url(message: Message, location_id):
    """Update the name for a location"""

    if message.text and "http" not in message.text:
        msg = bot.send_message(message.chat.id, dicts.events.wrong_location_url_text)
        bot.register_next_step_handler(msg, enter_new_location_url, location_id)

    if db_event.edit_location_url(location_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.url_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_location_url, location_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {location_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="2"))
def edit_location_none(call: CallbackQuery):
    """Edit location none"""

    print(f"We are in edit_location_none CALL DATA = {call.data}\n")
    *_, location_id = call.data.split(":")
    bot.send_sticker(
        call.message.chat.id,
        "CAACAgIAAxkBAAEUN15iiCeJU0iv22TLeXi_IU39-U4JWQACLgADa-18CgqvqjvoHnoDJAQ"    # Причесать дизайн
    )
    bot.send_message(call.message.chat.id, bot_speech.greetings(datetime.datetime.now().time().hour))


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="3"))
def delete_location(call: CallbackQuery):
    """DELETE location"""

    print(f"delete_location {call.data}")
    *_, location_id = call.data.split(":")

    item_name = db_event.search_location_by_id(location_id)[0]
    call_config = "delete_confirmation"
    item_type = "location"
    data = []
    msg = f"{dicts.changes.delete_confirmation_text}\n{item_name}?"

    for i, answer in enumerate(dicts.changes.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{location_id}:{i}"))

    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=keys.buttons.callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_suit_callback.filter(option_id="0"))
def edit_suit_name(call: CallbackQuery):
    """Edit suit name"""

    print(f"We are in edit_suit_name CALL DATA = {call.data}\n")
    *_, suit_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_suit_name_text)
    bot.register_next_step_handler(msg, enter_new_suit_name, suit_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_sticker(
    #     call.message.chat.id,
    #     "CAACAgIAAxkBAAEUN1RiiCW1_TMceKUYF5oulfjmOXpAYgACFgADa-18CgcoBnIvq3DlJAQ"    # Правильный код
    # )


def enter_new_suit_name(message: Message, suit_id):
    """Update the name for a suit"""

    if message.text and "/" in message.text:
        return

    if db_singer.edit_suit_name(suit_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.name_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_suit_name, suit_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {suit_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_suit_callback.filter(option_id="1"))
def edit_suit_photo(call: CallbackQuery):
    """Edit suit photo"""

    print(f"We are in edit_suit_name CALL DATA = {call.data}\n")
    *_, suit_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.drop_new_photo_text)
    bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_sticker(
    #     call.message.chat.id,
    #     "CAACAgIAAxkBAAEUN1RiiCW1_TMceKUYF5oulfjmOXpAYgACFgADa-18CgcoBnIvq3DlJAQ"    # Правильный код
    # )


def drop_new_suit_photo(message: Message, suit_id):
    """Update the photo for a suit"""

    if message.text and "/" in message.text:
        return

    if not message.photo:
        msg = bot.send_message(message.chat.id, dicts.changes.wrong_photo_format_text)
        bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
        return

    if len(message.photo) < 3:
        msg = bot.send_message(message.chat.id, dicts.changes.wrong_photo_format_text)
        bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
        return

    photo_file_id = message.photo[2].file_id

    if db_singer.edit_suit_photo(suit_id, photo_file_id):
        bot.send_message(message.chat.id, dicts.changes.photo_saved_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_suit_name, suit_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {suit_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_suit_callback.filter(option_id="2"))
def edit_suit_name(call: CallbackQuery):
    """DELETE suit"""

    *_, suit_id = call.data.split(":")

    item_name = db_singer.search_suits_by_id(suit_id)[0]
    call_config = "delete_confirmation"
    item_type = "suit"
    data = []
    msg = f"{dicts.changes.delete_confirmation_text}\n{item_name}?"

    for i, answer in enumerate(dicts.changes.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{suit_id}:{i}"))

    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=keys.buttons.callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.delete_confirmation_callback.filter())
def delete_item(call: CallbackQuery):
    """DELETE confirmation"""

    print(f"delete_item {call.data}")
    _, item_type, item_id, action_id = call.data.split(":")

    if action_id == "0":
        bot.send_sticker(
            call.message.chat.id,
            "CAACAgIAAxkBAAEUN3ZiiCzEII3_hNPQyD11w3B0BpjDFAACrAAD9wLID7sfK_VIr8n_JAQ"       # OK
        )
        # "CAACAgIAAxkBAAET3TlielLpoQABpzKmmwLZJd46cI8c74QAAh0AA2vtfArV9f-EEVC1CCQE"      # Не правки
        bot.delete_message(call.message.chat.id, call.message.id)
        return

    if item_type == "singer":
        db_singer.delete_singer(item_id)

    elif item_type == "event":
        db_event.delete_event(item_id)

    elif item_type == "location":
        db_event.delete_location_by_id(item_id)

    elif item_type == "song":
        db_songs.delete_song(item_id)

    elif item_type == "sheets":
        db_songs.delete_sheets_by_song_id(item_id)

    elif item_type == "sounds":
        db_songs.delete_sound_by_song_id(item_id)

    elif item_type == "suit":
        db_singer.delete_suit(item_id)

    bot.send_message(call.message.chat.id, dicts.changes.DELETED_text)
    bot.send_sticker(
        call.message.chat.id,
        "CAACAgIAAxkBAAET3TFielLLC-xjt4t8w12Gju8HUNrC-gACpgAD9wLID6sM5POpKsZYJAQ"       # Ha-ha-ha
    )
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.unblock_user_callback.filter())
def blacklist_user_remove(call: CallbackQuery):
    """Remove a user from the blacklist"""

    _, telegram_id = call.data.split(":")
    if db_singer.remove_user_from_blacklist(int(telegram_id)):
        bot.send_message(call.message.chat.id, dicts.changes.user_is_free_text)
    else:
        bot.send_message(call.message.chat.id, dicts.changes.ERROR_text)
    bot.delete_message(call.message.chat.id, call.message.id)
