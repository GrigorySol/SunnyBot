from datetime import datetime
from random import randint
from loader import bot
from database_control import db_singer
from database_control.db_event import search_event_by_id, search_location_by_id
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.callback_datas import suit_edit_callback, event_callback
from keyboards.inline.choice_buttons import new_singer_markup, joke_markup
from misc.edit_functions import display_suits, edit_suits
from misc.bot_speech import greetings
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


@bot.callback_query_handler(func=None, calendar_config=event_callback.filter())
def save_event(call: CallbackQuery):
    """Display info about the chosen event"""

    _, eid = call.data.split(":")
    print(search_event_by_id(eid))
    _, event_id, event_name, date, time, location_id, comment = search_event_by_id(eid)
    print(search_location_by_id(location_id))
    _, location_name, url = search_location_by_id(location_id)
    location = f"{location_name}\n\n{url}"
    bot.send_message(call.message.chat.id, location)
    msg = f"{event_name}\n{date} {time}\n"
    if comment:
        msg += comment
    bot.send_message(call.message.chat.id, msg)


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


@bot.message_handler(content_types=["audio"])
def handle_files(message: Message):
    """Print and send in message audio file_id"""

    audio_file_id = message.audio.file_id
    print(audio_file_id)
    bot.send_message(message.chat.id, audio_file_id)


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


@bot.message_handler(commands=["songs"])
def nothing_to_say(message: Message):
    bot.send_audio(message.chat.id,
                   "CQACAgIAAxkBAAIN-WJ075CgPoBkAuWjMVlTovjAYDa9AAJ6EgAC94eoS6EbqMZfgPQyJAQ")  # mp3


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


"""
@bot.callback_query_handler(func=None)
def remove_btn(call: CallbackQuery):
    # Close unused buttons
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""
