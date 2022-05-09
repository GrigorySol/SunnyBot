from datetime import datetime
from random import randint

from handlers.admin.admin_songs import edit_song_menu
from loader import bot
from database_control import db_singer, db_songs
from database_control.db_event import search_event_by_id, search_location_by_id, search_events_by_event_id
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.callback_datas import suit_edit_callback, event_callback,\
    song_info_callback, song_filter_callback, concert_filter_callback
from keyboards.inline.choice_buttons import new_singer_markup, joke_markup, change_buttons, callback_buttons
from misc.edit_functions import display_suits, edit_suits
from misc.bot_speech import greetings
from misc.messages.event_dictionary import MONTHS_CASE
from misc.messages.singer_dictionary import *
from misc.messages.joke_dictionary import *


@bot.message_handler(is_new_singer=True)
def singer_not_registered(message: Message):
    """Interact with a new user and offer to register"""

    singer_id = message.from_user.id
    singer_time = datetime.utcfromtimestamp(message.date).hour
    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(singer_time)}, Сашенька\n"
    else:
        text = f"{greetings(singer_time)}\n"
    text += not_registered_text
    bot.send_message(singer_id, text, reply_markup=new_singer_markup)


@bot.message_handler(commands=["voice"])
def show_voice(message: Message):
    """Display singer voices"""

    singer_id = db_singer.get_singer_id(message.from_user.id)
    voices = db_singer.get_singer_voices(singer_id)
    if not voices:
        bot.send_message(message.chat.id, no_voice_text)
    else:
        text = ", ".join(voice for _, voice in voices)
        bot.send_message(message.chat.id, f"Вы поёте в {text}.")


@bot.message_handler(commands=["suits"])
def show_suits(message: Message):
    """Display singer suits and buttons to add or remove"""
    sid = db_singer.get_singer_id(message.from_user.id)
    display_suits(message, sid)


@bot.callback_query_handler(func=None, singer_config=suit_edit_callback.filter())
def edit_suits_buttons(call: CallbackQuery):
    """Display buttons to add or remove suit"""
    edit_suits(call)


@bot.message_handler(commands=["songs"])
def show_songs(message: Message):
    """Display buttons for selecting the output of all songs, in work or concert program."""

    call_config = "song_filter"
    data = []
    for filter_id, text in enumerate(song_filter_text):
        data.append((text, f"{call_config}:{filter_id}"))

    bot.send_message(message.chat.id, chose_filter_text, reply_markup=callback_buttons(data, row=3))


@bot.callback_query_handler(func=None, singer_config=song_filter_callback.filter())
def edit_suits_buttons(call: CallbackQuery):
    """Display buttons with all song names, songs in work or upcoming concert program."""

    _, filter_id = call.data.split(":")
    data = []

    call_config = "song_info"
    msg = edit_text

    if filter_id == "0":
        songs = db_songs.get_all_songs()
        for song_id, song_name, _ in songs:
            data.append((song_name, f"{call_config}:{song_id}"))

    elif filter_id == "1":
        songs = db_songs.get_songs_in_work()
        for song_id, song_name, _ in songs:
            data.append((song_name, f"{call_config}:{song_id}"))

    else:
        concerts = search_events_by_event_id(2)
        call_config = "concert_filter"
        msg = chose_concert_text
        for concert_id, concert_name, date_time in concerts:
            concert_date = date_time.split(" ")[0]
            _, month, day = concert_date.split("-")
            name = f"{concert_name} {int(day)} {MONTHS_CASE[int(month)-1]}"
            data.append((name, f"{call_config}:{concert_id}"))

    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=concert_filter_callback.filter())
def edit_suits_buttons(call: CallbackQuery):
    """Display buttons with all song names, songs in work or upcoming concert programs."""

    _, event_id = call.data.split(":")
    data = []
    songs = db_songs.get_songs_by_event_id(event_id)
    call_config = "song_info"

    for song_id, song_name, _ in songs:
        data.append((song_name, f"{call_config}:{song_id}"))

    bot.send_message(call.message.chat.id, edit_text, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=song_info_callback.filter())
def show_song_info(call: CallbackQuery):
    """Show song info and allow admin to edit"""

    _, song_id = call.data.split(":")
    edit_song_menu(call.message, song_id, what_to_do_text)


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


@bot.callback_query_handler(func=None, calendar_config=event_callback.filter())
def show_event(call: CallbackQuery):
    """Display info about the chosen event"""

    _, eid = call.data.split(":")
    _, event_id, event_name, date_time, location_id, comment = search_event_by_id(eid)
    _, location_name, url = search_location_by_id(location_id)

    location = f"{location_name}\n\n{url}"
    bot.send_message(call.message.chat.id, location)
    date, time = date_time.split(" ")

    msg = f"{event_name}\n{date} в {time[0:5]}\n"
    if comment:
        msg += comment
    bot.send_message(call.message.chat.id, msg)

    # Admin can change the record about the event
    singer_id = call.from_user.id
    name = "event"

    if db_singer.is_admin(singer_id):
        bot.send_message(singer_id, edit_text, reply_markup=change_buttons(name, eid))


@bot.callback_query_handler(func=lambda c: c.data == 'close')
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.message_handler(func=lambda m: "скучно" in m.text.lower())
def back_btn(message: Message):
    """Send a random joke into the chat"""

    bot.register_next_step_handler(message, joking)
    bot.send_message(message.chat.id, do_you_wanna_my_joke_text,
                     reply_to_message_id=message.id, reply_markup=joke_markup)


def joking(message: Message):
    msg = randomizer(random_jokes_text)
    bot.send_message(message.chat.id, msg, reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    pass


# @bot.message_handler(content_types=["audio"])
# def handle_files(message: Message):
#     """Print and send in message audio file_id"""
#
#     audio_file_id = message.audio.file_id
#     print(message)
#     print(audio_file_id)
#     bot.send_message(message.chat.id, audio_file_id)


def check_commands(message: Message):
    if (message.text[0] == "/") or message.via_bot:
        return
    return message


@bot.message_handler(func=check_commands)
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""

    text = {randomizer(random_answer_text)}
    bot.forward_message(434767263, message.chat.id, message.id)
    print(message.text)
    print(text)
    bot.send_message(message.chat.id, text)


def randomizer(items):
    """Takes items and returns a random item"""
    i = randint(0, len(items) - 1)
    return items[i]


"""
@bot.callback_query_handler(func=None)
def remove_btn(call: CallbackQuery):
    # Close unused buttons
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""
