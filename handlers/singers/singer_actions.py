from datetime import datetime
from random import randint
from loader import bot
from db import BotDB
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.choice_buttons import new_singer_markup, joke_markup
from misc.bot_speech import greetings
from misc.bot_commands import singer_commands, admin_commands
from misc.bot_dictionary import *

BotDB = BotDB("sunny_bot.db")


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
    """TODO: Display callback buttons with voice"""
    voice = BotDB.search_singer_voice(message.from_user.id)[0][0]
    if not voice:
        bot.send_message(message.chat.id, no_voice_text)
    bot.send_message(message.chat.id, f"Вы поёте в {voice}.")


@bot.callback_query_handler(func=lambda c: c.data == 'close')
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.message_handler(func=lambda m: (m.text == 'скучно') or (m.text == 'Скучно'))
def back_btn(message: Message):
    bot.register_next_step_handler(message, joking)
    bot.send_message(message.chat.id, do_you_wanna_my_joke,
                     reply_to_message_id=message.id, reply_markup=joke_markup)


def joking(message: Message):
    msg = random_text(random_jokes)
    bot.send_message(message.chat.id, msg, reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    pass


def check_commands(message: Message):
    if message.text[0] == "/":
        return
    return message


@bot.message_handler(func=check_commands)
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""

    text = {random_text(random_answer_text)}
    bot.forward_message(434767263, message.chat.id, message.id)
    print(message.text)
    print(text)
    bot.send_message(message.chat.id, text)


def random_text(text: str):
    i = randint(0, len(text) - 1)
    return text[i]


"""
@bot.callback_query_handler(func=None)
def back_btn(call: CallbackQuery):
    # Close unused buttons
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""
