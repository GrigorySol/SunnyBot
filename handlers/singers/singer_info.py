from loader import bot
from db import BotDB
from telebot.types import CallbackQuery, Message
from keyboards.inline.callback_datas import search_callback
from misc.bot_dictionary import what_to_do

BotDB = BotDB("sunny_bot.db")


class SingerRegister:
    def __init__(self):
        self.singer_id = None
        self.singername = None
        self.name = None
        self.lastname = None


singer = SingerRegister()


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="singer"))
def display_singer_info(call: CallbackQuery):
    bot.send_message(call.from_user.id, what_to_do)
    if call.message:
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=None)
    singer_info(call)


def singer_info(call: CallbackQuery):
    """TODO: Display all info about the singer"""
    pass
