from loader import bot
import db
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import add_callback, remove_callback


@bot.callback_query_handler(func=None, singer_config=add_callback.filter())
def add_action(call: CallbackQuery):
    """Add singer's something to the database"""
    _, item, sid, suit_id = call.data.split(":")

    msg = "Что-то пошло не так с добавлением."

    if item == "suit":
        db.add_suit(sid, suit_id)
        msg = "Костюм добавлен!"

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)


@bot.callback_query_handler(func=None, singer_config=remove_callback.filter())
def remove_action(call: CallbackQuery):
    """Remove singer's something from the database"""
    _, item, sid, suit_id = call.data.split(":")

    msg = "Что-то пошло не так с удалением."

    if item == "suit":
        db.delete_suit(sid, suit_id)
        msg = "Костюм удалён!"

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg)
