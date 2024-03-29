import datetime
import inspect

import misc.dictionaries.buttons_dictionary
from config import VIP
from loader import bot, log
from telebot.types import CallbackQuery, Message
from misc import dicts, keys, tools, bot_speech
from misc.dictionaries import callback_dictionary as cd
from database_control import db_songs, db_singer, db_event, db_attendance


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="event"))
def display_event_options_to_change(call: CallbackQuery):
    """Display event options to change"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, item_id = call.data.split(":")

    # "Название", "Дату", "Время", "Место", "Комментарий", "УДАЛИТЬ"
    event = db_event.search_event_by_id(item_id)

    if not event:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.events.event_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    call_config = cd.selected_text
    if event[1] == 2:
        options = dicts.changes.edit_concert_text_tuple
    else:
        options = dicts.changes.edit_event_text_tuple

    tools.create_option_buttons(call.message, call_config, item_id, options)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="location"))
def display_location_options_to_change(call: CallbackQuery):
    """Display location options to change"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, item_id = call.data.split(":")

    location = db_event.search_location_by_id(int(item_id))

    if not location:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.events.location_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    msg = f"🧾 {location[0]}\n🗺 {location[1]}"
    bot.send_message(call.from_user.id, msg, disable_web_page_preview=True)

    call_config = cd.selected_location_text
    tools.create_option_buttons(call.message, call_config, item_id, dicts.changes.edit_location_text_tuple)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="suit"))
def display_suit_options_to_change(call: CallbackQuery):
    """Display suit options to change"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, item_id = call.data.split(":")

    suit = db_singer.search_suit_by_id(int(item_id))

    if not suit:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.changes.suit_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    call_config = cd.selected_suit_text
    tools.create_option_buttons(call.message, call_config, item_id, dicts.changes.edit_suit_text_tuple)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="0"))
def edit_event_name(call: CallbackQuery):
    """Edit name for an Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_event_name_text)
    bot.register_next_step_handler(msg, enter_new_event_name, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_event_time(message: Message, event_id: int, date):
    """Update the time for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text or message.text[0].isalpha():
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    time = message.text
    if '-' in time:
        hours, minutes = time.split("-")
        time = f"{hours}:{minutes}"
    elif ' ' in time:
        hours, minutes = time.split(" ")
        time = f"{hours}:{minutes}"
    elif ':' not in time:
        msg_data = bot.send_message(message.chat.id, dicts.events.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    print(f"enter_new_event_time {date} {time}")
    if db_event.event_datetime_exists(date, time):
        print("Time exists")
        msg_data = bot.send_message(message.chat.id, dicts.changes.event_time_busy)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    if db_event.edit_event_datetime(event_id, date, time):
        msg = dicts.changes.event_time_changed_text
        markup = keys.buttons.buttons_markup(event_id=event_id, menu_btn=True)
        bot.send_message(message.chat.id, msg, reply_markup=markup)


def enter_new_event_name(message: Message, event_id):
    """Update the name for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    event_type = db_event.get_event_by_id(event_id)[1]
    new_name = f"{dicts.events.event_type_pics_tuple[int(event_type)]} {message.text}"
    if db_event.edit_event_name(event_id, new_name):
        bot.send_message(message.chat.id, dicts.changes.name_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {new_name} {event_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="1"))
def edit_event_date(call: CallbackQuery):
    """Edit date for an Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    now = datetime.date.today()
    event_type = "4"  # edit
    markup = keys.calendar.generate_calendar_days(
        call.from_user.id, now.year, now.month, int(event_type), event_id
    )
    bot.send_message(call.message.chat.id, dicts.events.set_event_date_text, reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="2"))
def edit_event_time(call: CallbackQuery):
    """Edit time for an Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    event_date = db_event.get_event_date(event_id)
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_event_time_text)
    bot.register_next_step_handler(msg, enter_new_event_time, event_id, event_date)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="3"))
def edit_event_location(call: CallbackQuery):
    """Edit location for an Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")

    msg = dicts.events.choose_event_location_text
    bot.edit_message_text(
        msg, call.message.chat.id, call.message.id,
        reply_markup=keys.buttons.choose_location_buttons(event_id, go_menu=True)
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="4"))
def edit_comment_event(call: CallbackQuery):
    """Edit comment for an Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    comment = db_event.get_event_by_id(event_id)[6]
    if comment:
        bot.send_message(call.message.chat.id, comment)
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_comment_text)
    bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_event_comment(message: Message, event_id):
    """Update the comment for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if db_event.edit_event_comment(event_id, message.text):
        event = db_event.get_event_by_id(event_id)
        bot.send_message(message.chat.id, dicts.changes.comment_changed_text)
        call_config = cd.selected_text
        if event[1] == 2:
            options = dicts.changes.edit_concert_text_tuple
        else:
            options = dicts.changes.edit_event_text_tuple

        tools.create_option_buttons(message, call_config, event_id, options)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_event_comment, event_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {event_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="5"))
def edit_event_participant(call: CallbackQuery):
    """Edit Event participants"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    attendance_buttons(call, event_id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.show_participation_callback.filter())
def event_attendance(call: CallbackQuery):
    """Display singers attendance for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    attendance_buttons(call, event_id)


def attendance_buttons(call, event_id):
    attendance_data = []
    attendance_to_count = []
    for _, fullname, telegram_name, attendance in db_attendance.get_attendance_by_event_id(event_id):
        text = f"{dicts.attends.attendance_pics_tuple[int(attendance)]} {fullname}"
        attendance_data.append({"text": text, "callback_data": telegram_name})
        attendance_to_count.append(attendance)

    if attendance_data:
        statistic = f"{dicts.attends.attendance_text_tuple[0]} - {attendance_to_count.count(0)}\n" \
                    f"{dicts.attends.attendance_text_tuple[1]} - {attendance_to_count.count(1)}\n" \
                    f"{dicts.attends.attendance_text_tuple[2]} - {attendance_to_count.count(2)}"
        msg = f"{dicts.attends.attendant_singers_text}{statistic}"
        markup = keys.buttons.buttons_markup(attendance_data, event_id=event_id, menu_btn=True,
                                             participant=True)
    else:
        msg = dicts.attends.empty_attendance_text
        markup = keys.buttons.empty_participant_buttons(event_id)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="6"))
def delete_event(call: CallbackQuery):
    """DELETE Event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")

    item_name = db_event.get_event_name(event_id)
    item_type = "event"
    delete_confirmation_buttons(call, event_id, item_name, item_type)


def delete_confirmation_buttons(call, item_id, item_name, item_type):
    data = []
    call_config = cd.delete_confirmation_text
    msg = f"{dicts.changes.delete_confirmation_text} {item_name}?"
    for i, text in enumerate(dicts.changes.delete_confirmation_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{item_type}:{item_id}:{i}"})

    markup = keys.buttons.buttons_markup(data)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="7"))
def edit_concert_songs(call: CallbackQuery):
    """Edit songs for a concert"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, concert_id = call.data.split(":")
    call_config = cd.change_songs_text
    data = []
    msg = get_song_list(concert_id)

    msg += f"\n{dicts.singers.what_to_do_text}"

    for option_id, text in enumerate(dicts.changes.add_remove_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{concert_id}:{option_id}"})

        markup = keys.buttons.buttons_markup(data, event_id=concert_id, menu_btn=True)
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


def get_song_list(concert_id):
    songs = db_songs.get_songs_by_event_id(concert_id)
    msg = ""
    if songs:
        for _, song, _ in songs:
            msg += f"🎵 {song}\n"
    else:
        msg += f"{dicts.events.repertoire_is_empty_text}\n"
    return msg


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_callback.filter(option_id="8"))
def edit_concert_suit(call: CallbackQuery):
    """Show add or remove button to edit suit for a concert"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id = call.data.split(":")
    suit = db_event.get_suit_by_event_id(event_id)

    if suit:
        call_config = cd.remove_suit_text
        msg = dicts.changes.concert_suit_change_text
        markup = keys.buttons.buttons_markup([{"text": dicts.buttons.suit_change_btn_text,
                                               "callback_data": f"{call_config}:{event_id}:{suit[0]}"}])
        bot.send_photo(call.message.chat.id, suit[2], reply_markup=keys.buttons.close_markup)
        bot.send_message(call.message.chat.id, msg, reply_markup=markup)

    else:
        select_suit_for_concert(call, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def select_suit_for_concert(call, event_id):
    """Display all suits to choose for a concert"""

    suits = db_singer.get_suits_and_amount()
    singers_amount = db_singer.count_singers()
    if not singers_amount:
        singers_amount = 0

    msg = dicts.changes.choose_suit_text
    call_config = cd.select_suit_text
    data = []

    for suit_id, suit_name, photo, amount in suits:
        data.append(
            {"text": f"{amount}/{singers_amount} {suit_name}",
             "callback_data": f"{call_config}:{event_id}:{suit_id}"}
        )

    bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.remove_suit_callback.filter())
def display_suit_options_to_change(call: CallbackQuery):
    """Remove current concert suit and display suit options to change"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id, suit_id = call.data.split(":")
    db_event.remove_suit_from_concert(event_id, suit_id)
    select_suit_for_concert(call, event_id)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.change_songs_callback.filter())
def edit_songs_for_concert(call: CallbackQuery):
    """List of songs to edit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, concert_id, option_id = call.data.split(":")

    show_songs_for_concert(call.message, concert_id, option_id)


def show_songs_for_concert(message, concert_id, option_id):

    call_config = cd.concert_songs_text
    data = []

    if option_id == "0":
        option = "add"
        songs = db_songs.get_remain_songs(concert_id)
    else:
        option = "remove"
        songs = db_songs.get_songs_by_event_id(concert_id)

    for song_id, text, _ in songs:
        data.append({"text": text, "callback_data": f"{call_config}:{option}:{concert_id}:{song_id}"})

    msg = dicts.changes.add_remove_text_tuple[int(option_id)]
    markup = keys.buttons.buttons_markup(data, event_id=concert_id, menu_btn=True)
    bot.edit_message_text(msg, message.chat.id, message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, singer_config=keys.call.concert_songs_callback.filter())
def add_or_remove_songs(call: CallbackQuery):
    """Add or remove songs in concert program"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, option, concert_id, song_id = call.data.split(":")

    if option == "add":
        option_id = "0"
        if db_event.add_song_to_concert(concert_id, song_id):
            song_name = db_songs.get_song_name(song_id)
            bot.send_message(call.message.chat.id, f"{dicts.changes.song_added_to_concert_text} {song_name}")

        else:
            bot.send_message(call.message.chat.id, dicts.changes.song_already_added)

    else:
        option_id = "1"
        song_name = db_songs.get_song_name(song_id)
        db_event.remove_song_from_concert(concert_id, song_id)
        bot.send_message(call.message.chat.id, f"{dicts.changes.song_removed_from_concert} {song_name}")

    show_songs_for_concert(call.message, concert_id, option_id)


@bot.callback_query_handler(func=None, singer_config=keys.call.select_suit_callback.filter())
def change_suit_for_concert(call: CallbackQuery):
    """Add a suit for a concert"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, concert_id, suit_id = call.data.split(":")
    if db_event.add_suit_to_concert(concert_id, suit_id):
        bot.send_message(call.message.chat.id, dicts.changes.suit_added_text)

        call_config = cd.selected_text
        options = dicts.changes.edit_concert_text_tuple
        tools.create_option_buttons(call.message, call_config, concert_id, options)
        bot.delete_message(call.message.chat.id, call.message.id)

    else:
        bot.send_message(call.message.chat.id, dicts.changes.ERROR_text)
        bot.send_message(VIP, f"ERROR in {__name__}\nedit_suit_for_concert {call.data}")


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="0"))
def edit_location_name(call: CallbackQuery):
    """Edit location name"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, location_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_location_name_text)
    bot.register_next_step_handler(msg, enter_new_location_name, location_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_location_name(message: Message, location_id):
    """Update the name for a location"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
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

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, location_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_location_url_text)
    bot.register_next_step_handler(msg, enter_new_location_url, location_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_location_url(message: Message, location_id):
    """Update the name for a location"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "отмена" in message.text.lower():
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if "http" not in message.text:
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

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, location_id = call.data.split(":")
    bot.send_sticker(
        call.message.chat.id,
        "CAACAgIAAxkBAAEUN15iiCeJU0iv22TLeXi_IU39-U4JWQACLgADa-18CgqvqjvoHnoDJAQ"    # Причесать дизайн
    )
    bot.send_message(call.message.chat.id, bot_speech.greetings(datetime.datetime.now().time().hour))


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_location_callback.filter(option_id="3"))
def delete_location(call: CallbackQuery):
    """DELETE location"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, location_id = call.data.split(":")

    item_name = db_event.search_location_by_id(location_id)[0]
    item_type = "location"
    delete_confirmation_buttons(call, location_id, item_name, item_type)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_suit_callback.filter(option_id="0"))
def edit_suit_name(call: CallbackQuery):
    """Edit suit name"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, suit_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_suit_name_text)
    bot.register_next_step_handler(msg, enter_new_suit_name, suit_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_suit_name(message: Message, suit_id):
    """Update the name for a suit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
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

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, suit_id = call.data.split(":")
    msg = bot.send_message(call.message.chat.id, dicts.changes.drop_new_photo_text)
    bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
    bot.delete_message(call.message.chat.id, call.message.id)


def drop_new_suit_photo(message: Message, suit_id):
    """Update the photo for a suit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if not message.photo:
        msg = bot.send_message(message.chat.id, dicts.changes.wrong_photo_format_text)
        bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
        return

    if len(message.photo) < 3:
        msg = bot.send_message(message.chat.id, dicts.changes.wrong_photo_format_text)
        bot.register_next_step_handler(msg, drop_new_suit_photo, suit_id)
        return

    if db_singer.edit_suit_photo(suit_id, message.photo[2].file_id):
        bot.send_message(message.chat.id, dicts.changes.photo_saved_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_suit_name, suit_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {suit_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.selected_suit_callback.filter(option_id="2"))
def edit_suit_name(call: CallbackQuery):
    """DELETE suit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, suit_id = call.data.split(":")

    item_name = db_singer.search_suit_by_id(suit_id)[0]
    item_type = "suit"
    delete_confirmation_buttons(call, suit_id, item_name, item_type)


@bot.callback_query_handler(func=None, singer_config=keys.call.delete_confirmation_callback.filter())
def delete_item(call: CallbackQuery):
    """DELETE confirmation"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item_type, item_id, action_id = call.data.split(":")

    if action_id == "0":
        bot.send_sticker(
            call.message.chat.id,
            "CAACAgIAAxkBAAEUN3ZiiCzEII3_hNPQyD11w3B0BpjDFAACrAAD9wLID7sfK_VIr8n_JAQ"       # OK
        )
        # "CAACAgIAAxkBAAET3TlielLpoQABpzKmmwLZJd46cI8c74QAAh0AA2vtfArV9f-EEVC1CCQE"      # Не правки
        bot.delete_message(call.message.chat.id, call.message.id)
        return

    bot.send_message(call.message.chat.id, dicts.changes.DELETED_text)
    bot.send_sticker(
        call.message.chat.id,
        "CAACAgIAAxkBAAET3TFielLLC-xjt4t8w12Gju8HUNrC-gACpgAD9wLID6sM5POpKsZYJAQ"       # Ha-ha-ha
    )
    bot.delete_message(call.message.chat.id, call.message.id)

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
        from handlers.admin.admin_songs_and_suits import edit_song_menu
        edit_song_menu(call.message, item_id, misc.dicts.changes.edit_text)

    elif item_type == "sounds":
        db_songs.delete_sound_by_song_id(item_id)
        from handlers.admin.admin_songs_and_suits import edit_song_menu
        edit_song_menu(call.message, item_id, misc.dicts.changes.edit_text)

    elif item_type == "suit":
        db_singer.delete_suit(item_id)


@bot.callback_query_handler(func=None, singer_config=keys.call.unblock_user_callback.filter())
def blacklist_user_remove(call: CallbackQuery):
    """Remove a user from the blacklist"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, telegram_id = call.data.split(":")
    if db_singer.remove_user_from_blacklist(int(telegram_id)):
        bot.send_message(call.message.chat.id, dicts.changes.user_is_free_text)
    else:
        bot.send_message(call.message.chat.id, dicts.changes.ERROR_text)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.remove_participation_callback.filter())
def remove_participation(call: CallbackQuery):
    """Display singers to remove from an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    remove_participant_buttons(call, event_id)


def remove_participant_buttons(call, event_id):
    remove_data = [
        {"text": text, "callback_data": f"singer_attendance:remove:{event_id}:{singer_id}"}
        for singer_id, text, *_ in db_attendance.get_attendance_by_event_id(event_id)
    ]

    msg = dicts.attends.choose_singer_to_add_text
    markup = keys.buttons.buttons_markup(remove_data, event_id=event_id, menu_btn=True, participant=True)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_participant_callback.filter())
def add_participant(call: CallbackQuery):
    """Display singers to add into an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    add_participant_buttons(call, event_id)


def add_participant_buttons(call, event_id):

    add_data = [
        {"text": text, "callback_data": f"singer_attendance:add:{event_id}:{singer_id}"}
        for singer_id, text, _ in db_attendance.get_not_participating_by_event_id(event_id)
    ]

    msg = dicts.attends.choose_singer_to_add_text
    markup = keys.buttons.buttons_markup(add_data, event_id=event_id, menu_btn=True, participant=True)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_all_participants_callback.filter())
def add_all_participants(call: CallbackQuery):
    """Add all available singers with voices into an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"!!! {__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    db_attendance.add_all_singers_attendance(event_id)
    item_type = "event"
    markup = keys.buttons.show_participation_button(event_id)

    for buttons in keys.buttons.change_buttons(item_type, event_id).keyboard:
        markup.add(*buttons)
    msg = f"{dicts.attends.all_singers_added_text}\n{dicts.changes.need_something_text}"
    bot.send_message(call.message.chat.id, msg, reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.remove_all_participants_callback.filter())
def remove_all_participants(call: CallbackQuery):
    """Remove all singers from the event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"@@@ {__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    db_attendance.remove_all_singers_attendance(event_id)
    item_type = "event"
    markup = keys.buttons.show_participation_button(event_id)

    for buttons in keys.buttons.change_buttons(item_type, event_id).keyboard:
        markup.add(*buttons)
    msg = f"{dicts.attends.all_singers_removed_text}"
    bot.send_message(call.message.chat.id, msg, reply_markup=markup)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.singer_attendance_callback.filter(action="remove"))
def remove_singer_attendance(call: CallbackQuery):
    """Remove selected singer attendance from an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id, singer_id = call.data.split(":")
    singer_name = db_singer.get_singer_fullname(singer_id)

    if not db_attendance.get_singer_attendance_for_event(event_id, singer_id):
        bot.send_message(call.message.chat.id, f"{singer_name} {dicts.attends.singer_already_removed_text}")
        return

    db_attendance.remove_singer_attendance(event_id, singer_id)
    bot.send_message(call.message.chat.id, f"{singer_name} {dicts.attends.singer_removed_text}")
    remove_participant_buttons(call, event_id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.singer_attendance_callback.filter(action="add"))
def add_singer_attendance(call: CallbackQuery):
    """Add selected singer attendance from an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id, singer_id = call.data.split(":")
    singer_name = db_singer.get_singer_fullname(singer_id)

    if db_attendance.get_singer_attendance_for_event(event_id, singer_id):
        bot.send_message(call.message.chat.id, f"{singer_name} {dicts.attends.singer_already_added_text}")
        return

    db_attendance.add_singer_attendance(event_id, singer_id)
    bot.send_message(call.message.chat.id, f"{singer_name} {dicts.attends.singer_added_text}")
    add_participant_buttons(call, event_id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.singer_attendance_callback.filter(action="edit"))
def edit_singer_attendance(call: CallbackQuery):
    """Edit a singer attendance by a singer for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, event_id, decision = call.data.split(":")
    db_attendance.edit_singer_attendance(event_id, call.from_user.id, decision)
    event = db_event.get_event_by_id(event_id)
    bot.send_message(
        call.message.chat.id, f"{event[2]} на {event[3]} в {event[4]} "
                              f"{dicts.attends.set_attendance_text_tuple[int(decision)][0]} "
                              f"{dicts.attends.attendance_changed_text}"
    )
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, calendar_config=keys.call.mass_edit_attendance_callback.filter())
def mass_edit_singer_attendance(call: CallbackQuery):
    """Edit a singer attendance by a singer for an event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id, decision = call.data.split(":")
    db_attendance.edit_singer_attendance(event_id, call.from_user.id, decision)
    event = db_event.get_event_by_id(event_id)
    bot.send_message(
        call.message.chat.id, f"{event[2]} на {event[3]} в {event[4]} "
                              f"- {dicts.attends.set_attendance_text_tuple[int(decision)][0]}"
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.edit_admin_callback.filter())
def show_singers_admin(call: CallbackQuery):
    """Show singers to add or remove admin rights"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, option_id = call.data.split(":")
    display_singers_for_admin_rights(call, option_id)


@bot.callback_query_handler(func=None, singer_config=keys.call.add_remove_admin_callback.filter())
def add_or_remove_admin(call: CallbackQuery):
    """Add or remove admin rights for a singer"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, option_id, singer_id = call.data.split(":")

    if option_id == "0":
        db_singer.add_admin_by_singer_id(singer_id)
    else:
        db_singer.remove_admin(singer_id)

    display_singers_for_admin_rights(call, option_id)


def display_singers_for_admin_rights(call, option_id):
    call_config = cd.add_remove_admin_text

    if option_id == "0":
        singers = db_singer.get_all_non_admins()
        msg = dicts.singers.who_wants_to_leave_forever_text
    else:
        singers = db_singer.get_admins_fullname_singer_id()
        msg = dicts.singers.no_more_future_text
    data = [
        {"text": text, "callback_data": f"{call_config}:{option_id}:{singer_id}"}
        for text, singer_id in singers
    ]
    markup = keys.buttons.buttons_markup(data)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)
