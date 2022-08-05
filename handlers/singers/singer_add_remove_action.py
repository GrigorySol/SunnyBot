import inspect

from loader import bot, log
from database_control import db_singer
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import singer_add_callback, singer_remove_callback
from misc.edit_functions import display_suits, display_voices
from misc.messages.singer_dictionary import add_wrong_text, remove_wrong_text, suit_added_text,\
    suit_removed_text, voice_added_text, voice_removed_text


@bot.callback_query_handler(func=None, singer_config=singer_add_callback.filter())
def add_action(call: CallbackQuery):
    """Add singer's something to the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")

    if item == "suit":
        db_singer.add_singer_suit(singer_id, item_id)
        bot.send_message(call.message.chat.id, suit_added_text)
        display_suits(call.message, singer_id)

    elif item == "voice":
        db_singer.add_singer_voice(singer_id, item_id)
        bot.send_message(call.message.chat.id, voice_added_text)
        display_voices(call.message, singer_id)
    else:
        bot.send_message(call.message.chat.id, add_wrong_text)

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=singer_remove_callback.filter())
def remove_action(call: CallbackQuery):
    """Remove singer's something from the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, item, singer_id, item_id = call.data.split(":")

    if item == "suit":
        db_singer.remove_suit(singer_id, item_id)
        bot.send_message(call.message.chat.id, suit_removed_text)
        display_suits(call.message, singer_id)

    elif item == "voice":
        db_singer.remove_singer_from_voice(singer_id, item_id)
        bot.send_message(call.message.chat.id, voice_removed_text)
        display_voices(call.message, singer_id)
    else:
        bot.send_message(call.message.chat.id, remove_wrong_text)

    bot.delete_message(call.message.chat.id, call.message.id)
