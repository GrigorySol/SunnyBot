from loader import bot
from database_control import db_singer
from keyboards.inline.choice_buttons import callback_buttons
from misc.messages.singer_dictionary import edit_buttons_text, edit_text,\
    no_suit_text, too_many_suits, no_voice_text, too_many_voices


def display_suits(message, sid):
    suits = db_singer.get_singer_suits(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "suit"
    data = []

    for text in edit_buttons_text:
        data.append((text, f"{call_config}:{text}:{sid}"))

    if not suits:
        data.pop()
        msg = f"{no_suit_text} {edit_text}"

    elif len(db_singer.get_all_suits()) == len(suits):
        print(db_singer.get_all_suits())
        print(suits)
        data.pop(0)
        suit_names = []

        for _, name, photo in suits:
            suit_names.append(name)
            bot.send_photo(message.chat.id, photo, caption=name)
            bot.send_message(message.chat.id, "_____________________________")

        if db_singer.is_admin(message.from_user.id):
            msg = f"{singer_name} может взять на концерт "
        else:
            msg = f"Ваши костюмы: "
        msg += f"{', '.join(suit_names)}.\n{too_many_suits}\n{edit_text}"

    else:
        suit_names = []
        for _, name, photo in suits:
            suit_names.append(name)
            bot.send_photo(message.chat.id, photo, caption=name)
            bot.send_message(message.chat.id, "_____________________________")

        if db_singer.is_admin(message.from_user.id):
            msg = f"{singer_name} может взять на концерт "
        else:
            msg = f"Ваши костюмы: "
        msg += f"{', '.join(suit_names)}.\n{edit_text}"

    print(f"display_suits {data}")
    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


def display_voices(message, sid):
    voices = db_singer.get_singer_voices(sid)
    singer_name = db_singer.get_singer_fullname(sid)
    call_config = "voice"
    data = []

    for text in edit_buttons_text:
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

    print(f"display_voices {data}")
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
        suits = db_singer.get_all_suits()
        bot.send_message(call.message.chat.id, "_____________________________")
        for suit_id, name, photo in suits:
            available = db_singer.get_singer_suits(sid)
            if (suit_id, name, photo) in available:
                continue
            data.append((name, f"{call_config}:suit:{sid}:{suit_id}"))
            bot.send_photo(call.message.chat.id, photo, caption=name)
            bot.send_message(call.message.chat.id, "_____________________________")

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

