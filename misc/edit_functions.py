from loader import bot
from telebot.types import InputMediaPhoto
from database_control import db_singer
from keyboards.inline.choice_buttons import callback_buttons
from misc.messages.singer_dictionary import edit_text, no_suit_text, no_voice_text, too_many_voices
from misc.messages.changes_dictionary import edit_buttons_text_tuple


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
    for text in edit_buttons_text_tuple:
        data.append((text, f"{call_config}:{text}:{sid}"))

    if not suits:
        data.pop()
        msg = f"{no_suit_text} {edit_text}"
        bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))
        return

    elif len(db_singer.get_all_suits()) == len(suits):
        data.pop(0)

    if db_singer.is_admin(message.chat.id):
        msg = f"{singer_name} может взять на концерт "
    else:
        msg = f"Ваши костюмы: "

    msg += f"{', '.join(suit_names)}.\n{edit_text}"

    bot.send_media_group(message.chat.id, suit_data)
    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


def display_voices(message, sid):
    voices = db_singer.get_singer_voices(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "voice"
    data = []

    for text in edit_buttons_text_tuple:
        data.append((text, f"{call_config}:{text}:{sid}"))

    if not voices:
        data.pop()
        msg = f"{no_voice_text} {edit_text}"

    elif len(db_singer.get_all_voices()) == len(voices):
        data.pop(0)
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{too_many_voices}\n{edit_text}"

    else:
        voice_names = []
        for _, name in voices:
            voice_names.append(name)
        msg = f"{singer_name} поёт в {', '.join(voice_names)}.\n{edit_text}"

    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


def action_definition(action: str):
    """Define what choice made by singer"""

    if action == "Удалить":
        call_config = "singer_remove"
        msg = "Что удалить?"
    else:  # "Добавить"
        call_config = "singer_add"
        msg = "Что добавить?"
    return call_config, msg


def edit_suits(call):
    print(f"edit_suits {call.data}")
    _, action, sid = call.data.split(":")
    call_config, msg = action_definition(action)
    data = []

    if action == "Удалить":
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
    _, action, sid = call.data.split(":")
    call_config, msg = action_definition(action)
    data = []

    if action == "Удалить":
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

