from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import change_callback, selected_callback
from misc.messages.event_dictionary import select_option_to_change
from misc.messages.changes_dictionary import *
from misc.messages.singer_dictionary import NOTHING
from database_control import db_singer


@bot.callback_query_handler(func=None, calendar_config=change_callback.filter())
def display_options_to_change(call: CallbackQuery):
    """Display options to change"""

    print(f"We are in display_options_to_change CALL DATA = {call.data}\n")
    _, name, _id = call.data.split(":")
    call_config = "selected"

    if name == "event":         # "Посмотреть", "Мероприятие", "Концерт", "Репетицию", "Песню", "Жизнь"
        options = event_options_to_edit_text_tuple

    elif name == "location":    # "Название", "Ссылку на карту", "Ничего", "Надо подумать"
        options = location_options_to_edit_text_tuple

    else:                       # "Название", "Ноты", "Учебки", "Смысл"
        options = song_options_to_edit_text_tuple

    data = []
    for i, option in enumerate(options):
        data.append((option, f"{call_config}:{name}:{_id}:{i}"))
    bot.send_message(call.message.chat.id, select_option_to_change, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, calendar_config=selected_callback.filter())
def change_selected_option(call: CallbackQuery):
    """Ask to change an option"""
    print(f"change_selected_option DO NOTHING yet.\nData = {call}")
    _, name, _id, option_id = call.data.split(":")

    if name == "event":
        if option_id == "5":
            bot.send_message(call.message.chat.id, bot_cant_change_your_life_text)

    elif name == "location":
        pass

    else:
        if option_id == "5":
            bot.send_message(call.message.chat.id, bot_cant_change_maning)
    bot.send_message(call.message.chat.id, NOTHING)
