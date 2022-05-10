from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import change_callback, delete_confirmation_callback, \
    selected_event_callback, selected_location_callback
from misc.messages import event_dictionary as ev_d
from misc.messages import changes_dictionary as ch_d
from database_control import db_songs, db_singer, db_event


@bot.callback_query_handler(func=None, calendar_config=change_callback.filter())
def display_options_to_change(call: CallbackQuery):
    """Display options to change"""

    print(f"We are in display_options_to_change CALL DATA = {call.data}\n")
    _, name, item_id = call.data.split(":")

    if name == "event":  # "Посмотреть", "Мероприятие", "Концерт", "Репетицию", "Песню", "Жизнь"
        event = db_event.search_event_by_id(int(item_id))

        if not event:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, ev_d.event_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        call_config = "selected_event"
        options = ch_d.event_options_to_edit_text_tuple

    else:  # "location" - "Название", "Ссылку на карту", "Ничего", "УДАЛИТЬ
        location = db_event.search_location_by_id(int(item_id))

        if not location:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, ev_d.event_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        call_config = "selected_location"
        options = ch_d.location_options_to_edit_text_tuple

    data = []
    for option_id, option in enumerate(options):
        data.append((option, f"{call_config}:{option_id}:{item_id}"))

    bot.send_message(call.message.chat.id, ev_d.select_option_to_change, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=selected_event_callback.filter(option_id="5"))
def delete_event(call: CallbackQuery):
    """DELETE Event"""

    print(f"change_event_option {call.data}")
    _, option_id, _id = call.data.split(":")

    item_name = db_event.search_event_by_id(_id)[2]
    call_config = "delete_confirmation"
    item_type = "event"
    data = []
    msg = f"{ch_d.delete_confirmation_text} {item_name}?"

    for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{_id}:{i}"))

    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=selected_location_callback.filter(option_id="3"))
def delete_location(call: CallbackQuery):
    """DELETE location"""

    print(f"change_location_option {call.data}")
    _, option_id, _id = call.data.split(":")

    item_name = db_event.search_location_by_id(_id)[2]
    call_config = "delete_confirmation"
    item_type = "location"
    data = []
    msg = f"{ch_d.delete_confirmation_text}\n{item_name}?"

    for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
        data.append((answer, f"{call_config}:{item_type}:{_id}:{i}"))

    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, calendar_config=delete_confirmation_callback.filter())
def delete_item(call: CallbackQuery):
    """DELETE confirmation"""

    print(f"delete_item {call.data}")
    _, item_type, item_id, action_id = call.data.split(":")
    sticker_id = "CAACAgIAAxkBAAET3TFielLLC-xjt4t8w12Gju8HUNrC-gACpgAD9wLID6sM5POpKsZYJAQ"

    if action_id == "0":
        sticker_id = "CAACAgIAAxkBAAET3TlielLpoQABpzKmmwLZJd46cI8c74QAAh0AA2vtfArV9f-EEVC1CCQE"
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    if item_type == "singer":
        db_singer.delete_singer_by_id(int(item_id))

    elif item_type == "event":
        db_event.delete_event_by_id(int(item_id))

    elif item_type == "location":
        db_event.delete_location_by_id(int(item_id))

    elif item_type == "song":
        db_songs.delete_song_by_id(int(item_id))

    elif item_type == "sheets":
        db_songs.delete_sheets_by_song_id(int(item_id))

    elif item_type == "sounds":
        db_songs.delete_sounds_by_song_id(int(item_id))

    bot.send_message(call.message.chat.id, f"УДАЛЕНО! НАВСЕГДА!!! ХА-ха-ха-ха! ")
    bot.send_sticker(call.message.chat.id, sticker_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
