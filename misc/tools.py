from loader import bot
from config import VIP
from telebot.types import InputMediaPhoto
from keyboards.inline.choice_buttons import buttons_markup
from misc import dicts, keys
from database_control import db_singer


def display_suit_photos(message, suits):
    """
    Show group of the available suits photos
    """

    suit_data = []

    for _, name, photo in suits:
        suit_data.append(InputMediaPhoto(photo, name))

    for n in range(0, len(suit_data), 9):
        bot.send_media_group(message.chat.id, suit_data[n:n+9])


def generate_items_data_with_option(option, singer_id, items, item_type):
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


def generate_simple_items_data(call_config, items):
    data = [
        {"text": text, "callback_data": f"{call_config}:{item_id}"}
        for item_id, text, *args in items
    ]
    return data


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
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{dicts.singers.too_many_voices_text}\n" \
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


def create_option_buttons(message, call_config, item_id, options):
    data = []

    for option_id, text in enumerate(options):
        data.append({"text": text, "callback_data": f"{call_config}:{option_id}:{item_id}"})

    msg = dicts.changes.edit_text
    markup = keys.buttons.buttons_markup(data)
    bot.send_message(message.chat.id, msg, reply_markup=markup)


def admin_checker(message):
    """Restrict access for a non-admin singer."""

    is_admin = db_singer.is_admin(message.chat.id)
    if not is_admin and not VIP:
        bot.send_message(message.chat.id, dicts.singers.you_shell_not_pass_text)
        return False
    return True
