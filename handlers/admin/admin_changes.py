from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import change_callback, selected_callback, delete_confirmation_callback
from misc.messages.event_dictionary import select_option_to_change
from misc.messages.changes_dictionary import *
from misc.messages.singer_dictionary import NOTHING
from database_control import db_songs, db_singer, db_event


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
        bot.send_message(call.message.chat.id, NOTHING)

    else:
        if option_id == "5":
            bot.send_message(call.message.chat.id, bot_cant_change_maning)


@bot.callback_query_handler(func=None, calendar_config=delete_confirmation_callback.filter())
def delete_item(call: CallbackQuery):
    """DELETE confirmation"""

    print(f"delete_item {call.data}")
    _, item_type, item_name, item_id, action_id = call.data.split(":")
    sticker_id = "CAACAgIAAxkBAAET3TFielLLC-xjt4t8w12Gju8HUNrC-gACpgAD9wLID6sM5POpKsZYJAQ"

    if action_id == "0":
        sticker_id = "CAACAgIAAxkBAAET3TlielLpoQABpzKmmwLZJd46cI8c74QAAh0AA2vtfArV9f-EEVC1CCQE"
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    if item_type == "song":
        db_songs.delete_song_by_id(int(item_id))

    elif item_type == "sheets":
        db_songs.delete_sheets_by_song_id(int(item_id))

    elif item_type == "sounds":
        db_songs.delete_sounds_by_song_id(int(item_id))

    bot.send_message(call.message.chat.id, f"{item_name} УДАЛЕНО! НАВСЕГДА!!! ХА-ха-ха-ха! ")
    bot.send_sticker(call.message.chat.id, sticker_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
