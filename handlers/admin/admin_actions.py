import datetime

from loader import bot
from datetime import date
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from handlers.admin.admin_songs import add_sheets_or_sounds
from misc import dicts, keys
from database_control import db_singer, db_songs, db_event, db_attendance


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search singer options"""

    is_admin = db_singer.is_admin(message.from_user.id)
    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    amount = db_singer.count_singers()
    bot.send_message(message.chat.id,
                     f"В хоре {amount} певунов.\n{dicts.singers.show_singers_text}",
                     reply_markup=keys.buttons.search_choice_markup)


@bot.message_handler(commands=['add'])
def add_menu_handler(message: Message):
    """Show buttons to choose song or events"""

    print(f"calendar_command_handler")
    is_admin = db_singer.is_admin(message.from_user.id)
    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    call_config = "add_new"
    data = []
    for item_type, event in enumerate(dicts.events.to_add_text_tuple):
        if not item_type:
            continue
        data.append((event, f"{call_config}:{item_type}"))
    bot.send_message(
        message.chat.id, dicts.events.song_or_event_text, reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.message_handler(commands=['locations'])
def location_buttons_handler(message: Message):
    """Show location buttons for editing"""

    print(f"location_menu_handler")
    is_admin = db_singer.is_admin(message.chat.id)
    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    locations = db_event.get_all_locations()
    call_config = "change"
    item_type = "location"
    data = []

    for location_id, location_name, _ in locations:
        data.append((location_name, f"{call_config}:{item_type}:{location_id}"))

    bot.send_message(
        message.chat.id, dicts.events.choose_location_text, reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.message_handler(commands=["blacklist"])
def show_blacklist(message: Message):
    """Display blocked users to unblock"""

    is_admin = db_singer.is_admin(message.from_user.id)

    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    blocked_users = db_singer.get_all_blocked_users()

    if not blocked_users:
        bot.send_message(message.chat.id, dicts.changes.empty_blacklist_text)
        return

    call_config = "unblock_user"
    data = []

    for telegram_id, telegram_name in blocked_users:
        data.append((telegram_name, f"{call_config}:{telegram_id}"))

    bot.send_message(
        message.chat.id, dicts.changes.blacklist_text, reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.message_handler(commands=["magic"])
def show_blacklist(message: Message):
    """Add participation of all singers with voice"""

    is_admin = db_singer.is_admin(message.from_user.id)

    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    db_attendance.magic_attendance(date.today())
    msg = dicts.attends.magic_button_pressed_text
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=["menu_photo"])
def show_blacklist(message: Message):
    """Change menu screenshot"""

    is_admin = db_singer.is_admin(message.from_user.id)

    if not is_admin:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return

    msg = bot.send_message(message.chat.id, dicts.changes.drop_a_menu_photo_text)
    bot.register_next_step_handler(msg, edit_menu_photo_id)


def edit_menu_photo_id(message: Message):
    """Save photo file_id in the .env file in 'MENU_IMAGE' variable"""

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


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""

    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []

    for name, singer_id in singers:
        indicator = indicate_attendance(singer_id)
        data.append((f"{indicator} {name}", f"{call_config}:{singer_id}"))

    bot.send_message(
        call.message.chat.id, dicts.singers.show_all_singers_text, reply_markup=keys.buttons.callback_buttons(data)
    )
    bot.delete_message(call.message.chat.id, call.message.id)


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
def location_query(query: InlineQuery):
    """Inline User Search"""

    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []

    for i, (name, singer_id) in enumerate(singers):
        indicator = indicate_attendance(singer_id)
        if query.query.lower().strip() in name.lower():
            voices = ", ".join([voice for _, voice in db_singer.get_singer_voices(singer_id)])
            suits = ", ".join([suit for _, suit, _ in db_singer.get_singer_suits(singer_id)])
            if voices and suits:
                content = InputTextMessageContent(f"Голос: {voices}\nКостюмы: {suits}")
            elif voices:
                content = InputTextMessageContent(f"Голос: {voices}")
            elif suits:
                content = InputTextMessageContent(f"Костюмы: {suits}")
            else:
                content = InputTextMessageContent(f"У этого певуна ещё нет ни голоса, ни костюмов.")
            markup = keys.buttons.query_button(name, f"{call_config}:{singer_id}")
            data.append(InlineQueryResultArticle(i, f"{indicator} {name}", content, reply_markup=markup))

    bot.answer_inline_query(query.id, data)


@bot.callback_query_handler(func=None, calendar_config=keys.call.add_new_callback.filter())
def song_or_event(call: CallbackQuery):
    """Get id from data and call a song or an event creation."""

    print(f"song_or_event {call.data}")
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
