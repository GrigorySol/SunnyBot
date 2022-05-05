from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import singer_callback, info_callback, voice_edit_callback
from keyboards.inline.choice_buttons import singer_info_buttons
from misc.bot_dictionary import what_to_do, info_button_names
from misc.edit_functions import display_suits, display_voices
from misc.edit_functions import edit_voices
import db


@bot.callback_query_handler(func=None, singer_config=singer_callback.filter())
def display_singer_info(call: CallbackQuery):
    """Display info buttons"""
    sid = int(call.data.split(":")[1])
    singername = db.get_singer_telegram_name(sid)
    print(call.data)
    reply_markup = singer_info_buttons(singername, sid, info_button_names)
    if call.message:
        bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=None)
    bot.send_message(call.from_user.id, what_to_do, reply_markup=reply_markup)


@bot.callback_query_handler(func=None, singer_config=info_callback.filter())
def singer_menu(call: CallbackQuery):
    """Display """

    _, name, sid = call.data.split(":")
    sid = int(sid)
    print(call.data)

    if name == info_button_names[0]:            # Голос
        display_voices(call.message, sid)

    elif name == info_button_names[1]:          # Костюмы
        display_suits(call.message, sid)

    elif name == info_button_names[2]:          # Посещаемость
        msg = "Посещаемость пока отсутствует."
        bot.send_message(call.from_user.id, msg)

    elif name == info_button_names[3]:          # Комментарий
        msg = "Нечего комментировать."
        bot.send_message(call.from_user.id, msg)

    elif name == info_button_names[4]:          # УДАЛИТЬ
        msg = "Нельзя это удалить... пока."
        bot.send_message(call.from_user.id, msg)

    else:
        print(call.data)


@bot.callback_query_handler(func=None, singer_config=voice_edit_callback.filter())
def edit_voice_buttons(call: CallbackQuery):
    """Display buttons to add or remove voice"""
    edit_voices(call)
