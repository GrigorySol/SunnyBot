from loader import bot
from db import BotDB
from telebot.types import CallbackQuery, MessageEntity
from keyboards.inline.callback_datas import singer_callback, info_callback
from keyboards.inline.choice_buttons import singer_info_buttons
from misc.bot_dictionary import what_to_do, info_button_names

BotDB = BotDB("sunny_bot.db")


@bot.callback_query_handler(func=None, singer_config=singer_callback.filter())
def display_singer_info(call: CallbackQuery):
    """Display info buttons"""
    print(call.data)
    reply_markup = singer_info_buttons(call.from_user.username, info_button_names)
    # msg_entities = MessageEntity()
    if call.message:
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=None)
    bot.send_message(call.from_user.id, what_to_do, reply_markup=reply_markup)


@bot.callback_query_handler(func=None, singer_config=info_callback.filter())
def singer_voice(call: CallbackQuery):
    """Display the voice of a singer"""
    s_id = BotDB.get_singer_id(call.from_user.id)
    print(call.message.reply_markup.keyboard)
    if call.data == f"info:{info_button_names[0]}":     # Голос
        print(BotDB.get_singer_voices(s_id))
    elif call.data == f"info:{info_button_names[1]}":   # Костюмы
        pass
    elif call.data == f"info:{info_button_names[2]}":   # Посещаемость
        pass
    elif call.data == f"info:{info_button_names[3]}":   # Комментарий
        pass
    elif call.data == f"info:{info_button_names[4]}":   # УДАЛИТЬ
        pass
    else:
        print(call.data)


