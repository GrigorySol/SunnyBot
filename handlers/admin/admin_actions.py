from loader import bot
from datetime import date
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from keyboards.inline.choice_buttons import callback_buttons, search_choice_markup, query_button
from keyboards.inline.calendar_buttons import generate_calendar_days
from keyboards.inline.callback_datas import add_new_callback
from handlers.admin.admin_songs import add_sheets_or_sounds
from misc.messages.singer_dictionary import show_singers_text, you_shell_not_pass_text,\
    show_all_singers_text, CANCELED
from misc.messages.changes_dictionary import blacklist_text, empty_blacklist_text
from misc.messages.event_dictionary import set_event_date_text, events_to_add_text_tuple,\
    song_or_event_text, choose_location_text
from misc.messages.song_dictionary import enter_the_song_name_text, now_add_or_edit_text, song_name_exists_text
from database_control import db_singer, db_songs, db_event


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search singer options"""

    is_admin = db_singer.is_admin(message.from_user.id)
    if not is_admin:
        bot.send_message(message.chat.id, you_shell_not_pass_text)
        return

    amount = db_singer.count_singers()
    bot.send_message(message.chat.id, f"В хоре {amount} певунов.\n{show_singers_text}",
                     reply_markup=search_choice_markup)


@bot.message_handler(commands=['add'])
def add_menu_handler(message: Message):
    """Show buttons to choose song or events"""

    print(f"calendar_command_handler")
    is_admin = db_singer.is_admin(message.from_user.id)
    if not is_admin:
        bot.send_message(message.chat.id, you_shell_not_pass_text)
        return

    call_config = "add_new"
    data = []
    for i, event in enumerate(events_to_add_text_tuple):
        if not i:
            continue
        data.append((event, f"{call_config}:{i}"))
    bot.send_message(message.chat.id, song_or_event_text, reply_markup=callback_buttons(data))


@bot.message_handler(commands=['locations'])
def delete_menu_handler(message: Message):
    """Show location buttons for editing"""

    print(f"calendar_command_handler")
    is_admin = db_singer.is_admin(message.chat.id)
    if not is_admin:
        bot.send_message(message.chat.id, you_shell_not_pass_text)
        return

    locations = db_event.get_all_locations()
    call_config = "change"
    name = "location"
    data = []

    for location_id, location_name, _ in locations:
        data.append((location_name, f"{call_config}:{name}:{location_id}"))

    bot.send_message(message.chat.id, choose_location_text, reply_markup=callback_buttons(data))


@bot.message_handler(commands=["blacklist"])
def show_singers_search(message: Message):
    """Display callback buttons with search singer options"""

    is_admin = db_singer.is_admin(message.from_user.id)

    if not is_admin:
        bot.send_message(message.chat.id, you_shell_not_pass_text)
        return

    blocked_users = db_singer.get_all_blocked_users()

    if not blocked_users:
        bot.send_message(message.chat.id, empty_blacklist_text)
        return

    call_config = "unblock_user"
    data = []

    for user_id, telegram_name in blocked_users:
        data.append((telegram_name, f"{call_config}:{user_id}"))

    bot.send_message(message.chat.id, blacklist_text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""

    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []

    for singer in singers:
        data.append((singer[0], f"{call_config}:{singer[1]}"))

    bot.send_message(call.message.chat.id, show_all_singers_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.inline_handler(func=lambda query: len(query.query))
def location_query(query: InlineQuery):
    """Inline User Search"""

    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []

    for i, singer in enumerate(singers):
        if query.query.lower().strip() in singer[0].lower():
            voices = ", ".join([voice for _, voice in db_singer.get_singer_voices(singer[1])])
            suits = ", ".join([suit for _, suit, _ in db_singer.get_singer_suits(singer[1])])
            if voices and suits:
                content = InputTextMessageContent(f"Голос: {voices}\nКостюмы: {suits}")
            elif voices:
                content = InputTextMessageContent(f"Голос: {voices}")
            elif suits:
                content = InputTextMessageContent(f"Костюмы: {suits}")
            else:
                content = InputTextMessageContent(f"У этого певуна ещё нет ни голоса, ни костюмов.")
            btn = query_button(singer[0], f"{call_config}:{singer[1]}")
            data.append(InlineQueryResultArticle(i, singer[0], content, reply_markup=btn))

    bot.answer_inline_query(query.id, data)


@bot.callback_query_handler(func=None, calendar_config=add_new_callback.filter())
def song_or_event(call: CallbackQuery):
    """Get id from data and call a song or an event creation"""

    print(f"song_or_event {call.data}")
    _, _id = call.data.split(":")
    if _id == "4":
        msg = bot.send_message(call.message.chat.id, enter_the_song_name_text)
        bot.register_next_step_handler(msg, add_song_name)

    else:
        """Show calendar buttons"""
        now = date.today()
        bot.send_message(call.message.chat.id, set_event_date_text,
                         reply_markup=generate_calendar_days(now.year, now.month, int(_id)))


def add_song_name(message: Message):
    """Save the song name to the database and call buttons to edit the song name/sounds/sheets"""

    if "/" in message.text:
        bot.send_message(message.chat.id, CANCELED)

    elif db_songs.song_name_exists(message.text):
        msg = bot.send_message(message.chat.id, song_name_exists_text)
        bot.register_next_step_handler(msg, add_song_name)

    else:
        song_id = db_songs.add_song(message.text)
        msg = bot.send_message(message.chat.id, now_add_or_edit_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, int(song_id))
