from loader import bot
from db import BotDB
from telebot.types import CallbackQuery, Message
from keyboards.inline.callback_datas import search_callback, info_callback
from keyboards.inline.choice_buttons import singer_info_buttons
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
    """Display info buttons"""
    if call.message:
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=singer_info_buttons(call.from_user.username))
    else:
        bot.send_message(call.from_user.id, what_to_do, reply_markup=singer_info_buttons(call.from_user.username))


@bot.callback_query_handler(func=None, singer_config=info_callback.filter(type="voice"))
def singer_voice(call: CallbackQuery):
    """Display the voice of a singer"""
    print(call)
