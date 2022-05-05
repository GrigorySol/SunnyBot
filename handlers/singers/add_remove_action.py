from loader import bot
import db
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import add_callback, remove_callback
from misc.bot_dictionary import add_wrong, remove_wrong, suit_added, suit_removed, voice_added, voice_removed


@bot.callback_query_handler(func=None, singer_config=add_callback.filter())
def add_action(call: CallbackQuery):
    """Add singer's something to the database"""
    _, item, sid, item_id = call.data.split(":")
    print(f"{item}, {sid}, {item_id}, {call.data}")

    msg = add_wrong

    if item == "suit":
        db.add_suit(sid, item_id)
        msg = suit_added

    elif item == "voice":
        db.add_voice(sid, item_id)
        msg = voice_added

    elif item == "song":
        pass

    elif item == "event":
        pass

    elif item == "rehearsal":
        pass

    elif item == "concert":
        pass

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)


@bot.callback_query_handler(func=None, singer_config=remove_callback.filter())
def remove_action(call: CallbackQuery):
    """Remove singer's something from the database"""
    _, item, sid, item_id = call.data.split(":")
    print(f"{item}, {sid}, {item_id}, {call.data}")

    msg = remove_wrong

    if item == "suit":
        db.delete_suit(sid, item_id)
        msg = suit_removed

    elif item == "voice":
        db.delete_voice(sid, item_id)
        msg = voice_removed

    elif item == "song":
        pass

    elif item == "event":
        pass

    elif item == "rehearsal":
        pass

    elif item == "concert":
        pass

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)
