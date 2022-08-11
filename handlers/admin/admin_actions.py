import datetime
import inspect

from loader import bot, log, JOKES
from datetime import date
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from handlers.admin.admin_songs_and_suits import add_sheets_or_sounds
from misc import dicts, keys, tools
from misc.dictionaries import callback_dictionary as cd
from database_control import db_singer, db_songs, db_event, db_attendance


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search singer options"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    amount = db_singer.count_singers()
    bot.send_message(message.chat.id,
                     f"В хоре {amount} певунов.\n{dicts.singers.show_singers_text}",
                     reply_markup=keys.buttons.search_choice_markup)


@bot.message_handler(commands=['add'])
def add_options(message: Message):
    """Show buttons to choose event, song or suit to add"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    call_config = cd.add_new_text
    data = []
    for item_type, text in enumerate(dicts.events.to_add_text_tuple):
        if not item_type:
            continue
        data.append({"text": text, "callback_data": f"{call_config}:{item_type}"})
    bot.send_message(
        message.chat.id, dicts.events.song_or_event_text, reply_markup=keys.buttons.buttons_markup(data)
    )


@bot.message_handler(commands=['locations'])
def location_buttons(message: Message):
    """Show location buttons for editing"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t{message.id}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    locations = db_event.get_all_locations()
    call_config = cd.change_item_text
    item_type = "location"
    data = []

    for location_id, text, _ in locations:
        data.append({"text": text, "callback_data": f"{call_config}:{item_type}:{location_id}"})

    bot.send_message(
        message.chat.id, dicts.events.choose_location_text,
        reply_markup=keys.buttons.buttons_markup(data)      # find the way to fix this
    )


@bot.message_handler(commands=["admins"])
def show_admins(message: Message):
    """Show admin list. Ask to add/remove admins."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t{message.id}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    admins = db_singer.get_all_admins()
    msg = "\n".join([
        db_singer.get_singer_fullname(db_singer.get_singer_id(telegram_id[0]))
        for telegram_id in admins
    ])
    call_config = cd.admin_edit_text
    data = [
        {"text": text, "callback_data": f"{call_config}:{option_id}"}
        for option_id, text in enumerate(dicts.changes.add_remove_text_tuple)
    ]
    msg = f"{dicts.singers.admins_text}\n{msg}"
    markup = keys.buttons.buttons_markup(data)
    bot.send_message(message.chat.id, msg, reply_markup=markup)


@bot.message_handler(commands=["blacklist"])
def show_blacklist(message: Message):
    """Display blocked users to unblock"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    blocked_users = db_singer.get_all_blocked_users()

    if not blocked_users:
        bot.send_message(message.chat.id, dicts.changes.empty_blacklist_text)
        return

    call_config = cd.unblock_user_text
    data = []

    for telegram_id, text in blocked_users:
        data.append({"text": text, "callback_data": f"{call_config}:{telegram_id}"})

    bot.send_message(
        message.chat.id, dicts.changes.blacklist_text, reply_markup=keys.buttons.buttons_markup(data)
    )


@bot.message_handler(commands=["magic"])
def full_participation(message: Message):
    """Add participation of all singers with voice"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    db_attendance.magic_attendance(date.today())
    msg = dicts.attends.magic_button_pressed_text
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["menu_photo"])
def menu_tutorial(message: Message):
    """Change menu screenshot"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    msg = bot.send_message(message.chat.id, dicts.changes.drop_a_menu_photo_text)
    bot.register_next_step_handler(msg, edit_menu_photo_id)


@bot.message_handler(commands=["joke"])
def add_joke(message: Message):
    """Change menu screenshot"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not tools.admin_checker(message):
        return

    msg = bot.send_message(message.chat.id, dicts.changes.add_joke_text)
    bot.register_next_step_handler(msg, add_new_joke)


def edit_menu_photo_id(message: Message):
    """Save photo file_id in the .env file in 'MENU_IMAGE' variable"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.photo:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return
    try:
        file = open(".env")
        data_list = file.readlines()
        file.close()

        data_list[-1] = f"MENU_IMAGE={message.photo[-1].file_id}"

        file = open(".env", "w")
        file.write("".join(data_list))
        file.close()

        bot.send_message(message.chat.id, dicts.changes.added_menu_photo_text)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, e)


def add_new_joke(message: Message):
    """Save a joke into joke file"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return
    try:
        file = open("jokes.txt", "a")
        file.write(repr(message.text) + '\n')
        file.close()
        JOKES.append(repr(message.text))
        bot.send_message(message.chat.id, dicts.changes.joke_saved_text)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, e)


@bot.callback_query_handler(func=lambda c: c.data == cd.singer_show_all_text)
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    singers = db_singer.get_all_singers()
    call_config = cd.singer_display_text
    data = []

    for name, singer_id in singers:
        indicator = indicate_attendance(singer_id)
        data.append({"text": f"{indicator} {name}", "callback_data": f"{call_config}:{singer_id}"})

    msg = dicts.singers.show_all_singers_text
    markup = keys.buttons.buttons_markup(data)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


def indicate_attendance(singer_id):
    """
    Calculate the singer's attendance percentage for the last month.
    Return colored indicators: 🔴 (0-30), 🟡 (30-80), 🟢 (80+) or 🟣 if not yet attended.
    """

    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    attend = db_attendance.get_attendance_by_interval(singer_id, start_date, end_date)

    if not attend:
        return dicts.attends.attendance_indicator_text_tuple[3]

    attended = sum([int(i) for i in attend if int(i) == 1])
    percent_attend = 100 // (len(attend) / attended) if attended else 0

    if percent_attend < 30:
        return dicts.attends.attendance_indicator_text_tuple[0]
    elif 30 < percent_attend < 80:
        return dicts.attends.attendance_indicator_text_tuple[1]
    else:
        return dicts.attends.attendance_indicator_text_tuple[2]


@bot.inline_handler(func=lambda query: len(query.query))
def song_query(query: InlineQuery):
    """Inline Song Search"""

    call_config = cd.song_info_text
    songs = db_songs.get_all_songs()
    data = []

    for i, (song_id, name, comment) in enumerate(songs):

        if query.query.lower().strip() in name.lower():
            sheets = len(db_songs.get_sheets_by_song_id(song_id))
            records = len(db_songs.get_sound_by_song_id(song_id))
            if comment:
                content = InputTextMessageContent(f"Нот: {sheets}. Учебок: {records}.\n{comment}")
            else:
                content = InputTextMessageContent(f"Нот: {sheets}. Учебок: {records}.")

            image_url = "https://images-na.ssl-images-amazon.com/images/I/71EodKggiQL.png"
            markup = keys.buttons.query_button(name, f"{call_config}:{song_id}")
            data.append(InlineQueryResultArticle(i, f"🎵 {name}", content, reply_markup=markup, thumb_url=image_url))

    bot.answer_inline_query(query.id, data)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_new_callback.filter())
def add_new_item(call: CallbackQuery):
    """Get id from data and start an event/song/suit/location creation."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item_type = call.data.split(":")
    if item_type == "4":
        """Add location"""
        msg_data = bot.send_message(call.message.chat.id, dicts.events.enter_location_url_text)
        from handlers.admin.admin_event import check_location_url
        bot.register_next_step_handler(msg_data, check_location_url)

    elif item_type == "5":
        """Add song"""
        msg = bot.send_message(call.message.chat.id, dicts.songs.enter_the_song_name_text)
        bot.register_next_step_handler(msg, add_song_name)

    elif item_type == "6":
        """Add suit"""
        msg = bot.send_message(call.message.chat.id, dicts.singers.enter_the_suit_name_text)
        bot.register_next_step_handler(msg, add_suit_name)

    else:
        """For events show calendar buttons"""
        now = date.today()

        bot.send_message(
            call.message.chat.id,
            dicts.events.set_event_date_text,
            reply_markup=keys.calendar.generate_calendar_days(
                call.from_user.id, now.year, now.month, int(item_type)
            )
        )

    bot.delete_message(call.message.chat.id, call.message.id)


def add_song_name(message: Message):
    """Save the song name to the database and call buttons to edit the song name/sounds/sheets."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    elif db_songs.song_name_exists(message.text):
        msg = bot.send_message(message.chat.id, dicts.songs.song_name_exists_text)
        bot.register_next_step_handler(msg, add_song_name)

    else:
        song_id = db_songs.add_song(message.text)
        msg = bot.send_message(message.chat.id, dicts.songs.add_sheets_or_sounds_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, int(song_id))


def add_suit_name(message: Message):
    """Check if the suit name exists and ask to upload an image."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    elif db_singer.suit_name_exists(message.text):
        msg = bot.send_message(message.chat.id, dicts.singers.suit_name_exists_text)
        bot.register_next_step_handler(msg, add_suit_name)

    else:
        msg = bot.send_message(message.chat.id, dicts.singers.add_suit_photo_text)
        bot.register_next_step_handler(msg, save_new_suit, message.text)


def save_new_suit(message: Message, suit_name):

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if not message.photo:
        msg = bot.send_message(message.chat.id, dicts.singers.no_photo_text)
        bot.register_next_step_handler(msg, save_new_suit, suit_name)
        return

    if len(message.photo) < 3:
        msg = bot.send_message(message.chat.id, dicts.changes.wrong_photo_format_text)
        bot.register_next_step_handler(msg, save_new_suit, suit_name)
        return

    else:
        db_singer.add_suit(suit_name, message.photo[2].file_id)
        bot.send_message(message.chat.id, dicts.singers.new_suit_added_text)
