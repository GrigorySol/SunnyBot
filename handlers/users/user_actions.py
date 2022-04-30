from datetime import datetime
from loader import bot
from db import BotDB
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import new_user_markup, search_choice
from keyboards.inline.callback_datas import search_callback
from misc.bot_speech import greetings, random_answer
from misc.bot_dictionary import *

BotDB = BotDB("sunny_bot.db")


# If the user is not in the database
@bot.message_handler(is_new_user=True)
def user_not_registered(message: Message):
    user_id = message.from_user.id
    user_time = datetime.utcfromtimestamp(message.date).hour
    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(user_time)}, Сашенька\n"
    else:
        text = f"{greetings(user_time)}\n"
    text += not_registered_text
    bot.send_message(user_id, text, reply_markup=new_user_markup)


@bot.message_handler(commands=["singers"])
def show_users(message: Message):
    amount = BotDB.count_users()
    bot.send_message(message.from_user.id,
                     f"В хоре {amount} певунов.\n {show_users_text}",
                     reply_markup=search_choice)


@bot.message_handler(commands=["voice"])
def show_voice(message: Message):
    voice = BotDB.search_user_voice(message.from_user.id)[0][0]
    if not voice:
        bot.send_message(message.from_user.id, no_voice_text, reply_markup=search_choice)
    bot.send_message(message.from_user.id, f"Вы состоите в {voice}.")


@bot.callback_query_handler(func=None, user_config=search_callback.filter(type="user_name"))
def search_by_user_name(call: CallbackQuery):
    bot.send_message(call.from_user.id, enter_name_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_users(call: CallbackQuery):
    bot.send_message(call.from_user.id, show_all_users_text)
    singers = BotDB.show_users()
    for singer in singers:
        msg = f"{singer[1]} {singer[2]} @{singer[0]}"
        if len(singer) > 3:
            msg += f" ({singer[3]})"
        bot.send_message(call.from_user.id, msg)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'cancel')
def cancel_btn(call: CallbackQuery):
    bot.send_message(call.from_user.id, cancel_btn_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    bot.send_message(call.from_user.id, back_btn_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


# If nothing to say
@bot.message_handler()
def nothing_to_say(message: Message):
    text = {random_answer()}                            # \n\n{nothing_to_say_text}
    print(message.text)
    print(text)
    bot.send_message(message.from_user.id, text)
