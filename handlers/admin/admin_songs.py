from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaAudio, InputMediaDocument
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import edit_song_callback, edit_song_material_callback
from misc.messages.changes_dictionary import song_options_to_edit_text_tuple
from misc.messages.singer_dictionary import edit_buttons_text, NOTHING
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
        call_config = "edit_song_material"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for edit_id, text in enumerate(edit_buttons_text):
            data.append((text, f"{call_config}:{song_id}:{option_id}:{edit_id}"))

        if sheets:
            for sh in sheets:
                sheets_data.append(InputMediaDocument(sh[3]))
            bot.send_media_group(call.message.chat.id, sheets_data)
            msg = add_or_delete_text

        else:
            data.pop()
            msg = not_net_text

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    elif option_id == "2":
        print(f"edit_song_options {option_id}")
        sounds = db_songs.get_sound_by_song_id(song_id)
        call_config = "edit_song_material"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for edit_id, text in enumerate(edit_buttons_text):
            data.append((text, f"{call_config}:{song_id}:{option_id}:{edit_id}"))

        if sounds:
            for sound in sounds:
                sheets_data.append(InputMediaAudio(sound[3]))
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
        bot.send_message(message.chat.id, SONG_WRONG_TEXT)


@bot.callback_query_handler(func=None, calendar_config=edit_song_material_callback.filter())
def edit_song_materials(call: CallbackQuery):
    """Add or Remove sheets and sounds for a song"""

    print(f"edit_song_materials {call.data}")
    _, song_id, option_id, edit_id = call.data.split(":")

    def _add():
        msg = bot.send_message(call.message.chat.id, drop_the_file_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    def _delete():
        if option_id == "1":
            print("TODO: delete sheets")
            bot.send_message(call.message.chat.id, NOTHING)

        elif option_id == "2":
            print("TODO: delete sounds")
            bot.send_message(call.message.chat.id, NOTHING)

        else:
            bot.send_message(call.message.chat.id, SONG_WRONG_TEXT)

    if edit_id == "0":
        _add()

    elif edit_id == "1":
        _delete()

    else:
        bot.send_message(call.message.chat.id, SONG_WRONG_TEXT)


def add_sheets_or_sounds(message: Message, song_id):
    """Manage batch or a single file upload processing"""

    if message.document:        # sheets
        doc_file_id = message.document.file_id
        voice_id = message.document.file_name[-1]

        if voice_id.isdigit() and int(voice_id):
            voice_id = int(voice_id)
        else:
            voice_id = None

        print(f"add_sheets_or_sounds {doc_file_id}")
        db_songs.add_sheets(song_id, voice_id, doc_file_id)
        msg = bot.send_message(message.chat.id, sheets_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    elif message.audio:      # sounds
        audio_file_id = message.audio.file_id
        voice_id = message.audio.file_name[-1]

        if voice_id.isdigit() and int(voice_id):
            voice_id = int(voice_id)
        else:
            voice_id = None

        print(f"add_sheets_or_sounds {audio_file_id}")
        db_songs.add_sound(song_id, voice_id, audio_file_id)
        msg = bot.send_message(message.chat.id, audio_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    else:
        edit_song_menu(message, song_id, something_else)


def edit_song_menu(message, song_id, msg):
    options = song_options_to_edit_text_tuple
    call_config = "edit_song"
    data = []
    for i, option in enumerate(options):
        data.append((option, f"{call_config}:{song_id}:{i}"))
    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))
