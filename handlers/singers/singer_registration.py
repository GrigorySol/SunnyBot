from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import register_callback
from misc.bot_dictionary import *
from db import BotDB

BotDB = BotDB("sunny_bot.db")


class SingerRegister:
    def __init__(self):
        self.singer_id = None
        self.singername = None
        self.name = None
        self.lastname = None


singer = SingerRegister()


@bot.callback_query_handler(func=None, singer_config=register_callback.filter())
def add_new_singer(call: CallbackQuery):
    msg = bot.send_message(call.message.chat.id, enter_your_name)
    bot.register_next_step_handler(msg, singer_name_step)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def singer_name_step(message: Message):
    name = message.text
    if " " in name and len(name) > 3:
        name, lastname = name.split(" ")
        singer.singer_id = message.from_user.id
        singer.singername = message.from_user.username
        bot.send_message(message.chat.id, thanks_for_register)
        BotDB.add_singer(singer.singer_id, singer.singername, name, lastname)
        print(f"New singer {name} {lastname} registered")
    elif name.isdigit():
        msg = bot.send_message(message.chat.id, name_is_digit)
        bot.register_next_step_handler(msg, singer_name_step)

    elif len(name) < 2 or " " in name:
        msg = bot.send_message(message.chat.id, name_too_short)
        bot.register_next_step_handler(msg, singer_name_step)
    else:
        singer.singer_id = message.from_user.id
        singer.singername = message.from_user.username
        singer.name = name
        msg = bot.send_message(message.chat.id, enter_your_lastname)
        bot.register_next_step_handler(msg, singer_lastname_step)


def singer_lastname_step(message: Message):
    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.chat.id, lastname_is_digit)
        bot.register_next_step_handler(msg, singer_lastname_step)
    else:
        singer.lastname = lastname
        bot.send_message(message.chat.id, thanks_for_register)
        BotDB.add_singer(singer.singer_id, singer.singername, singer.name, singer.lastname)
        print(f"New singer {singer.name} {singer.lastname} registered")
