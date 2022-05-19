from config import VIP
from loader import bot
from telebot.types import InputMediaPhoto, Message
from keyboards.inline.choice_buttons import callback_buttons
from misc.messages import event_dictionary as ev_d, singer_dictionary as sin_d, changes_dictionary as ch_d
from database_control import db_singer, db_event


def display_suits(message, sid):
    """
    Receive message data and a singer id from the database
    Show group of the available suits photos and write the text
    """

    suits = db_singer.get_singer_suits(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "suit"
    data = []
    suit_names = []
    suit_data = []

    for _, name, photo in suits:
        suit_names.append(name)
        suit_data.append(InputMediaPhoto(photo, name))

    # add/remove/close buttons
    for i, text in enumerate(ch_d.edit_buttons_text_tuple):
        data.append((text, f"{call_config}:{i}:{sid}"))

    if not suits:
        data.pop()
        msg = f"{sin_d.no_suit_text} {sin_d.edit_text}"
        bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))
        return

    elif len(db_singer.get_all_suits()) == len(suits):
        data.pop(0)

    if db_singer.is_admin(message.chat.id):
        msg = f"{singer_name} может взять на концерт "
    else:
        msg = f"Ваши костюмы: "

    msg += f"{', '.join(suit_names)}.\n{sin_d.edit_text}"

    bot.send_media_group(message.chat.id, suit_data)
    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


def display_voices(message, sid):
    voices = db_singer.get_singer_voices(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "voice"
    data = []

    for i, text in enumerate(ch_d.edit_buttons_text_tuple):
        data.append((text, f"{call_config}:{i}:{sid}"))

    if not voices:
        data.pop()
        msg = f"{sin_d.no_voice_text} {sin_d.edit_text}"

    elif len(db_singer.get_all_voices()) == len(voices):
        data.pop(0)
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{sin_d.too_many_voices}\n{sin_d.edit_text}"

    else:
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{sin_d.edit_text}"

    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


def action_definition(action: str):
    """Define what choice made by singer"""

    if action == "0":  # "Добавить"
        call_config = "singer_add"
        msg = "Что добавить?"
    else:   # УДАЛИТЬ
        call_config = "singer_remove"
        msg = "Что удалить?"
    return call_config, msg


def edit_suits(call):
    print(f"edit_suits {call.data}")
    _, action_id, sid = call.data.split(":")
    call_config, msg = action_definition(action_id)
    data = []

    if action_id == "1":
        suits = db_singer.get_singer_suits(sid)
        for suit_id, name, _ in suits:
            data.append((name, f"{call_config}:suit:{sid}:{suit_id}"))

    else:
        suit_data = []
        suits = db_singer.get_all_suits()
        for suit_id, name, photo in suits:
            available = db_singer.get_singer_suits(sid)
            if (suit_id, name, photo) in available:
                continue
            data.append((name, f"{call_config}:suit:{sid}:{suit_id}"))
            suit_data.append(InputMediaPhoto(photo, name))
        bot.send_media_group(call.message.chat.id, suit_data)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))


def edit_voices(call):
    print(f"edit_voice {call.data}")
    _, action_id, sid = call.data.split(":")
    call_config, msg = action_definition(action_id)
    data = []

    if action_id == "1":
        voices = db_singer.get_singer_voices(sid)
        for voice_id, name in voices:
            data.append((name, f"{call_config}:voice:{sid}:{voice_id}"))

    else:
        voices = db_singer.get_all_voices()
        for voice_id, name in voices:
            available = db_singer.get_singer_voices(sid)
            if (voice_id, name) in available:
                continue
            data.append((name, f"{call_config}:voice:{sid}:{voice_id}"))

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))


def enter_new_event_time(message: Message, _id, date):
    """Update the time for an event"""

    time = message.text
    if '-' in time:
        hours, minutes = time.split("-")
        time = f"{hours}:{minutes}"
    elif ' ' in time:
        hours, minutes = time.split(" ")
        time = f"{hours}:{minutes}"
    elif ':' not in time:
        msg_data = bot.send_message(message.chat.id, ev_d.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    print(f"enter_new_event_time {date} {time}")
    if db_event.event_datetime_exists(date, time):
        print("Time exists")
        msg_data = bot.send_message(message.chat.id, ch_d.event_time_busy)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    if db_event.edit_event_datetime(_id, date, time):
        bot.send_message(message.chat.id, ch_d.event_time_changed_text)
