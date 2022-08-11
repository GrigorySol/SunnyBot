import inspect

from handlers.singers.singer_actions import edit_singer_suits
from loader import bot, log
from database_control import db_singer
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import singer_add_callback, singer_remove_callback
from misc.tools import display_voices
from misc import dicts


@bot.callback_query_handler(func=None, singer_config=singer_add_callback.filter(item_type="suit"))
def add_singer_suit(call: CallbackQuery):
    """Add singer's suit to the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")
    db_singer.add_singer_suit(singer_id, item_id)
    bot.send_message(call.message.chat.id, dicts.singers.suit_added_text)
    edit_singer_suits(call.message)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=singer_add_callback.filter(item_type="voice"))
def add_singer_voice(call: CallbackQuery):
    """Add singer's voice to the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")

    db_singer.add_singer_voice(singer_id, item_id)
    bot.send_message(call.message.chat.id, dicts.singers.voice_added_text)
    display_voices(call.message, singer_id)

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=singer_remove_callback.filter(item_type="suit"))
def remove_singer_suit(call: CallbackQuery):
    """Remove singer's suit from the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")

    db_singer.remove_suit(singer_id, item_id)
    bot.send_message(call.message.chat.id, dicts.singers.suit_removed_text)
    edit_singer_suits(call.message)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=singer_remove_callback.filter(item_type="voice"))
def remove_singer_voice(call: CallbackQuery):
    """Remove singer's voice from the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")

    db_singer.remove_singer_from_voice(singer_id, item_id)
    bot.send_message(call.message.chat.id, dicts.singers.voice_removed_text)
    display_voices(call.message, singer_id)

    bot.delete_message(call.message.chat.id, call.message.id)
