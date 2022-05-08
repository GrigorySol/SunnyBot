from loader import bot
from database_control import db_singer
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import singer_add_callback, singer_remove_callback
from misc.edit_functions import display_suits, display_voices
from misc.messages.singer_dictionary import add_wrong_text, remove_wrong_text, suit_added_text,\
    suit_removed_text, voice_added_text, voice_removed_text


@bot.callback_query_handler(func=None, singer_config=singer_add_callback.filter())
def add_action(call: CallbackQuery):
    """Add singer's something to the database"""
    _, item, sid, item_id = call.data.split(":")
    print(f"{item}, {sid}, {item_id}, {call.data}")

    msg = add_wrong_text

    if item == "suit":
        db_singer.add_suit(sid, item_id)
        msg = suit_added_text
        display_suits(call.message, sid)

    elif item == "voice":
        db_singer.add_voice(sid, item_id)
        msg = voice_added_text
        display_voices(call.message, sid)

    elif item == "event":
        pass

    elif item == "rehearsal":
        pass

    elif item == "concert":
        pass

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)


@bot.callback_query_handler(func=None, singer_config=singer_remove_callback.filter())
def remove_action(call: CallbackQuery):
    """Remove singer's something from the database"""
    _, item, sid, item_id = call.data.split(":")
    print(f"{item}, {sid}, {item_id}, {call.data}")

    msg = remove_wrong_text

    if item == "suit":
        db_singer.delete_suit(sid, item_id)
        msg = suit_removed_text
        display_suits(call.message, sid)

    elif item == "voice":
        db_singer.delete_voice(sid, item_id)
        msg = voice_removed_text
        display_voices(call.message, sid)

    elif item == "event":
        pass

    elif item == "rehearsal":
        pass

    elif item == "concert":
        pass

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)
