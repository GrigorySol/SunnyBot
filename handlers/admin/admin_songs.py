from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaAudio, InputMediaDocument
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import edit_song_callback
from misc.messages.singer_dictionary import edit_buttons_text
from misc.messages.song_dictionary import *
from database_control import db_songs


@bot.callback_query_handler(func=None, calendar_config=edit_song_callback.filter())
def edit_song_options(call: CallbackQuery):
    """Manage song edit options: Name, Sheets and Sound"""
    print(f"edit_song_options {call.data}")
    _, song_id, option_id = call.data.split(":")

    if option_id == "0":
        print(f"edit_song_options {option_id}")
        msg = bot.send_message(call.message.chat.id, enter_new_name_text)
        bot.register_next_step_handler(msg, enter_new_song_name, song_id)

    elif option_id == "1":
        print(f"edit_song_options {option_id}")
        sheets = db_songs.get_sheets_by_song_id(song_id)
        call_config = "sheets"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for i, text in enumerate(edit_buttons_text):
            data.append((text, f"{call_config}:{song_id}:{i}"))

        if sheets:
            for sh in sheets:
                sheets_data.append(InputMediaDocument(sh))
            bot.send_media_group(call.message.chat.id, sheets_data)
            msg = add_or_delete_text

        else:
            data.pop()
            msg = not_net_text

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    elif option_id == "2":
        print(f"edit_song_options {option_id}")
        sounds = db_songs.get_sound_by_song_id(song_id)
        call_config = "sounds"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for i, text in enumerate(edit_buttons_text):
            data.append((text, f"{call_config}:{song_id}:{i}"))

        if sounds:
            for sound in sounds:
                sheets_data.append(InputMediaAudio(sound))
            bot.send_media_group(call.message.chat.id, sheets_data)
            msg = add_or_delete_text

        else:
            data.pop()
            msg = not_sound_text

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    else:
        bot.send_message(call.message.chat.id, meaning_text)


def enter_new_song_name(message: Message, song_id):
    """UPDATE the song name in the database"""

    print(f"enter_new_song_name {song_id}, {message.text}")
    if db_songs.edit_song_name(song_id, message.text):
        bot.send_message(message.chat.id, song_name_changed_text)
    else:
        bot.send_message(message.chat.id, song_name_change_failed_text)
