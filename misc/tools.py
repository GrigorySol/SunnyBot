from loader import bot
from config import VIP
from telebot.types import InputMediaPhoto, Message
from keyboards.inline.choice_buttons import buttons_markup
from misc import dicts, keys
from database_control import db_singer, db_event


def display_suit_photos(message, suits):
    """
    Show group of the available suits photos
    """

    suit_data = []

    for _, name, photo in suits:
        suit_data.append(InputMediaPhoto(photo, name))

    for n in range(0, len(suit_data), 9):
        bot.send_media_group(message.chat.id, suit_data[n:n+9])


def generate_items_data(option, singer_id, items, item_type):
    """Generates msg and data to add ot remove items for a singer."""

    if option == "add":
        msg = dicts.changes.what_to_add_text
        call_config = dicts.call_dic.singer_add_action_text
    else:
        msg = dicts.changes.what_to_remove_text
        call_config = dicts.call_dic.singer_remove_action_text

    data = [
        {"text": text, "callback_data": f"{call_config}:{item_type}:{singer_id}:{item_id}"}
        for item_id, text in items
    ]

    return msg, data


def display_voices(message, sid):
    voices = db_singer.get_singer_voices(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "voice"
    data = []

    for i, text in enumerate(dicts.changes.add_remove_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{i}:{sid}"})

    if not voices:
        data.pop()
        msg = f"{dicts.singers.no_voice_text}"

    elif len(db_singer.get_all_voices()) == len(voices):
        data.pop(0)
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{dicts.singers.too_many_voices}\n" \
              f"{dicts.changes.edit_text}"

    else:
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{dicts.changes.edit_text}"

    bot.send_message(message.chat.id, msg, reply_markup=buttons_markup(data))


def edit_voices(call):
    print(f"edit_voice {call.data}")
    _, action_id, sid = call.data.split(":")
    data = []

    if action_id == "1":
        msg = dicts.changes.what_to_remove_text
        call_config = dicts.call_dic.singer_remove_action_text
        voices = db_singer.get_singer_voices(sid)
        for voice_id, text in voices:
            data.append({"text": text, "callback_data": f"{call_config}:voice:{sid}:{voice_id}"})

    else:
        msg = dicts.changes.what_to_add_text
        call_config = dicts.call_dic.singer_add_action_text
        voices = db_singer.get_all_voices()
        for voice_id, text in voices:       # TODO: change it
            available = db_singer.get_singer_voices(sid)
            if (voice_id, text) in available:
                continue
            data.append({"text": text, "callback_data": f"{call_config}:voice:{sid}:{voice_id}"})

    bot.send_message(call.message.chat.id, msg, reply_markup=buttons_markup(data))


def enter_new_event_time(message: Message, event_id: int, date):
    """Update the time for an event"""

    if not message.text or "/" in message.text or message.text[0].isalpha():
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    time = message.text
    if '-' in time:
        hours, minutes = time.split("-")
        time = f"{hours}:{minutes}"
    elif ' ' in time:
        hours, minutes = time.split(" ")
        time = f"{hours}:{minutes}"
    elif ':' not in time:
        msg_data = bot.send_message(message.chat.id, dicts.events.wrong_event_time_text)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    print(f"enter_new_event_time {date} {time}")
    if db_event.event_datetime_exists(date, time):
        print("Time exists")
        msg_data = bot.send_message(message.chat.id, dicts.changes.event_time_busy)
        bot.register_next_step_handler(msg_data, enter_new_event_time)
        return

    if db_event.edit_event_datetime(event_id, date, time):
        msg = dicts.changes.event_time_changed_text
        markup = keys.buttons.buttons_markup(event_id=event_id, menu_btn=True)
        bot.send_message(message.chat.id, msg, reply_markup=markup)


def admin_checker(message):
    """Restrict access for a non-admin singer."""

    is_admin = db_singer.is_admin(message.chat.id)
    if not is_admin and not VIP:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return False
    return True
