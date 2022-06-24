import datetime
from random import randint

import misc.messages.buttons_dictionary
from config import VIP, VIP2
from loader import bot
from database_control import db_singer, db_songs, db_event, db_attendance
from telebot.custom_filters import TextFilter
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from misc.edit_functions import display_suits, edit_suits
from misc import dicts, keys, callback_dict as cd


@bot.callback_query_handler(func=None, singer_config=keys.call.buttons_roll_callback.filter())
def rolling_callback_buttons(call: CallbackQuery):
    """Roll a page with buttons"""

    print(f"buttons_rolling {call.data}")
    _, direction, btn_type, index, event_id = call.data.split(":")

    if not keys.buttons.keep_data.row:
        bot.edit_message_text(dicts.changes.ERROR_text, call.message.chat.id, call.message.id, reply_markup=None)
        return

    if direction == "previous":
        keys.buttons.keep_data.i -= 1
    elif direction == "next":
        keys.buttons.keep_data.i += 1

    if btn_type == "call":
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.id,
            reply_markup=keys.buttons.callback_buttons(keys.buttons.keep_data.data, keys.buttons.keep_data.row, True)
        )

    elif btn_type == "url":
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.id,
            reply_markup=keys.buttons.participant_message_buttons(keys.buttons.keep_data.data,
                                                                  event_id, keys.buttons.keep_data.row, True)
        )


@bot.message_handler(commands=["voice"])
def show_voice(message: Message):
    """Display singer voices"""

    singer_id = db_singer.get_singer_id(message.from_user.id)
    voices = db_singer.get_singer_voices(singer_id)
    if not voices:
        bot.send_message(message.chat.id, dicts.singers.no_voice_text)
    else:
        text = ", ".join(voice for _, voice in voices)
        bot.send_message(message.chat.id, f"Вы поёте в {text}.")


@bot.message_handler(commands=["suits"])
def show_suits(message: Message):
    """Display singer suits and buttons to add or remove"""
    singer_id = db_singer.get_singer_id(message.from_user.id)
    display_suits(message, singer_id)

    if db_singer.is_admin(message.from_user.id):
        call_config = cd.display_suits_text
        data = [(dicts.changes.button_show_all_suits_text, f"{call_config}")]
        msg = f"{misc.messages.buttons_dictionary.admin_buttons_text}\n{dicts.changes.show_all_suits_text}"
        bot.send_message(message.chat.id, msg, reply_markup=keys.buttons.callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.suit_edit_callback.filter())
def edit_suits_buttons(call: CallbackQuery):
    """Display buttons to add or remove suit"""
    edit_suits(call)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(commands=["songs"])
def chose_song_filter(message: Message):
    """Display buttons for selecting the output of all songs, in work or concert program."""

    call_config = cd.song_filter_text
    data = []
    for filter_id, text in enumerate(dicts.singers.song_filter_text_tuple):
        data.append((text, f"{call_config}:{filter_id}"))

    bot.send_message(
        message.chat.id, dicts.singers.choose_filter_text, reply_markup=keys.buttons.callback_buttons(data)
    )


@bot.callback_query_handler(func=None, singer_config=keys.call.song_filter_callback.filter())
def show_songs(call: CallbackQuery):
    """Display buttons with all song names, songs in work or upcoming concerts."""

    _, filter_id = call.data.split(":")
    data = []
    call_config = cd.song_info_text

    if filter_id == "0":
        songs = db_songs.get_all_songs()

    elif filter_id == "1":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=365)
        songs = db_songs.get_songs_in_work(2, f"{start_date}", f"{end_date}")

    else:
        concerts = db_event.search_events_by_event_type(2)
        call_config = cd.concert_filter_text
        for concert_id, concert_name, date, _ in concerts:
            _, month, day = date.split("-")
            name = f"{concert_name} {int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]}"
            data.append((name, f"{call_config}:{concert_id}"))
        bot.send_message(
            call.message.chat.id, dicts.singers.choose_concert_text, reply_markup=keys.buttons.callback_buttons(data)
        )
        bot.delete_message(call.message.chat.id, call.message.id)
        return

    if songs:
        for song_id, song_name, _ in songs:
            data.append((song_name, f"{call_config}:{song_id}"))
        bot.send_message(
            call.message.chat.id, dicts.songs.which_song_text, reply_markup=keys.buttons.callback_buttons(data)
        )
    else:
        bot.send_message(call.message.chat.id, dicts.songs.no_songs_text)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.concert_filter_callback.filter())
def concert_songs(call: CallbackQuery):
    """Display buttons with song names for a concert program."""

    _, event_id = call.data.split(":")
    data = []
    songs = db_songs.get_songs_by_event_id(event_id)
    call_config = cd.song_info_text

    if songs:
        for song_id, song_name, _ in songs:
            data.append((song_name, f"{call_config}:{song_id}"))

        bot.send_message(
            call.message.chat.id, dicts.songs.which_song_text, reply_markup=keys.buttons.callback_buttons(data)
        )

    else:
        bot.send_message(call.message.chat.id, dicts.songs.no_songs_text)

    # Admin can change the record about the event
    singer_id = call.from_user.id

    if db_singer.is_admin(singer_id):
        msg = f"{misc.messages.buttons_dictionary.admin_buttons_text}\n{dicts.songs.wanna_add_text}"
        bot.send_message(
            call.message.chat.id,
            msg,
            reply_markup=keys.buttons.add_concert_songs_buttons(event_id)
        )
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(commands=["events"])
def nothing_to_say(message: Message):
    bot.send_sticker(message.chat.id,
                     "CAACAgIAAxkBAAETnXxicIxNf0TYCRSrmzD9SD-iTjSr1QAClBQAAsBCeEsVRtvoCLXI0iQE")


@bot.message_handler(commands=["rehearsal"])
def nothing_to_say(message: Message):
    bot.send_sticker(message.chat.id,
                     "CAACAgIAAxkBAAETnX5icIyDshGmTfhQFatW5TJnbJkjkQACtBoAApsZwUq8_BZS0faNxyQE")


@bot.message_handler(commands=["concerts"])
def nothing_to_say(message: Message):
    bot.send_audio(message.chat.id,
                   "CQACAgIAAxkBAAETnYJicIzUt04joDIy7_uLOkUpHENW3wACKBoAAhFE4UpblvEevwxe_yQE")


@bot.callback_query_handler(func=None, calendar_config=keys.call.show_event_callback.filter())
def show_event(call: CallbackQuery):
    """Display info about the chosen event"""

    _, event_id = call.data.split(":")
    _, event_type, event_name, event_date, time, location_id, comment = db_event.search_event_by_id(event_id)
    location_data = db_event.search_location_by_id(location_id)
    telegram_id = call.from_user.id
    print(f"singer_actions show_event\n"
          f"{call.from_user.username} {call.from_user.first_name} {call.from_user.last_name} {call.data}\n"
          f"{event_name} {event_date} {time}\n")

    _, month, day = event_date.split("-")
    event_date_text = f"{int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]}"

    msg = f"{event_name} {event_date_text} в {time}\n"

    if location_data:
        msg += f"{dicts.events.location_text} {location_data[0]}\n"
        bot.send_message(telegram_id, location_data[1], reply_markup=keys.buttons.close_markup)

    if event_type == 2:
        songs = db_songs.get_songs_by_event_id(event_id)
        suit = db_event.get_suit_by_event_id(event_id)

        if suit:
            msg += f"\n{dicts.events.suit_for_event_text}\n{suit[1]}\n"

        msg += f"\n{dicts.events.repertoire_text}\n"
        if songs:
            for _, song, _ in songs:
                msg += f"🎵 {song}\n"
        else:
            msg += f"{dicts.events.repertoire_is_empty_text}\n"

    if comment:
        msg += f"\n{dicts.events.comment_text}\n{comment}\n"

    # ask a singer to set the attendance
    singer_id = db_singer.get_singer_id(telegram_id)

    attendance = db_attendance.get_singer_attendance_for_event(event_id, singer_id)
    if attendance:
        call_config = cd.singer_attendance_text
        data = [
            (text, f"{call_config}:edit:{event_id}:{i}")
            for i, text in enumerate(dicts.attends.set_attendance_text_tuple)
        ]
        if attendance[0] == 0 or attendance[0] == 1:
            msg += f"\n{dicts.attends.chosen_attendance_text}\n" \
                   f"{dicts.attends.set_attendance_text_tuple[attendance[0]]}\n" \
                   f"\n{dicts.attends.wanna_change_text}"
        else:
            msg += f"\n{dicts.attends.select_attendance_text}"

        bot.send_message(telegram_id, msg, reply_markup=keys.buttons.callback_buttons(data))

    elif telegram_id != int(VIP) and telegram_id != int(VIP2):
        msg += f"\n{dicts.attends.you_not_participate_text}"
        bot.send_message(telegram_id, msg)

    else:
        bot.send_message(telegram_id, msg)

    # Admin can change the record about the event
    if db_singer.is_admin(telegram_id):
        item_type = "event"
        markup = keys.buttons.show_participation(event_id)

        for buttons in keys.buttons.change_buttons(item_type, event_id).keyboard:
            markup.add(*buttons)

        msg = f"{misc.messages.buttons_dictionary.admin_buttons_text}\n{dicts.changes.need_something_text}"
        bot.send_message(telegram_id, msg, reply_markup=markup)

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda c: c.data == cd.close_text)
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.calendar_text_list, ignore_case=True))
def calendar_message(message: Message):
    """Answer to type a command /calendar"""
    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.calendar_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.songs_text_list, ignore_case=True))
def song_message(message: Message):
    """Answer to type a command /songs"""

    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.song_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.suits_text_list, ignore_case=True))
def suit_message(message: Message):
    """Answer to type a command /suits"""

    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.suit_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.boring_text_list, ignore_case=True))
def boring_message(message: Message):
    """Send a random joke into the chat"""

    if message.via_bot:
        return
    bot.register_next_step_handler(message, joking)
    bot.send_message(message.chat.id, dicts.singers.do_you_wanna_my_joke_text,
                     reply_to_message_id=message.id, reply_markup=keys.buttons.accept_markup)


@bot.message_handler(text=TextFilter(contains=dicts.filters.fool_text_list, ignore_case=True))
def fool_message(message: Message):
    """Answer for the fool"""

    if message.via_bot:
        return
    msg = randomizer(dicts.jokes.embarrassed_text_tuple)
    bot.send_message(message.chat.id, msg, reply_to_message_id=message.id)


def joking(message: Message):
    msg = randomizer(dicts.jokes.random_jokes_text_tuple)
    bot.send_message(message.chat.id, msg, reply_markup=ReplyKeyboardRemove())


def check_commands(message: Message):
    if (message.text[0] == "/") or message.via_bot:
        return
    return message


@bot.message_handler(func=check_commands)
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""

    text = randomizer(dicts.jokes.random_answer_text_tuple)
    bot.forward_message(VIP, message.chat.id, message.id, disable_notification=True)
    bot.send_message(VIP, text, disable_notification=True)
    bot.send_message(message.chat.id, text)


def randomizer(items):
    """Takes items and returns a random item"""
    i = randint(0, len(items) - 1)
    return items[i]
