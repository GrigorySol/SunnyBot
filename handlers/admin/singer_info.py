from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import singer_callback, info_callback
from keyboards.inline.choice_buttons import singer_info_buttons, callback_buttons
from misc.bot_dictionary import what_to_do, info_button_names, edit_buttons, no_suit_text, edit_suit_text
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
    """Display the voice of a singer"""
    _, name, sid = call.data.split(":")
    sid = int(sid)
    print(call.data)

    if name == info_button_names[0]:            # Голос
        voices = db.get_singer_voices(sid)
        print(voices)
        if bool(voices):
            bot.send_message(call.from_user.id, voices)
        else:
            bot.send_message(call.from_user.id, "Здесь ничего нет")
    elif name == info_button_names[1]:          # Костюмы
        suits = db.get_singer_suits(sid)
        call_config = "suit"
        data = []
        for text in edit_buttons:
            data.append((text, f"{call_config}:{text}:{sid}"))
        if not suits:
            data.pop()
            msg = f"{no_suit_text}\n{edit_suit_text}"
        else:
            msg = f"Костюмы в наличии {suits}.\n{edit_suit_text}"
        print(data)
        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
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
