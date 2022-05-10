from loader import bot
from telebot.types import Message, CallbackQuery, InputMediaAudio, InputMediaDocument
from keyboards.inline.choice_buttons import callback_buttons
from keyboards.inline.callback_datas import edit_song_callback, edit_song_material_callback, song_info_callback
from misc.messages import changes_dictionary as ch_d
from misc.messages.singer_dictionary import NOTHING, CANCELED, edit_text, you_shell_not_pass_text
from misc.messages import song_dictionary as song_d
from database_control import db_songs, db_singer


@bot.callback_query_handler(func=None, calendar_config=song_info_callback.filter())
def show_song_info(call: CallbackQuery):
    """Show song info and allow admin to edit"""

    is_admin = db_singer.is_admin(call.message.chat.id)
    if not is_admin:
        bot.send_message(call.message.chat.id, you_shell_not_pass_text)
        return

    _, song_id = call.data.split(":")
    edit_song_menu(call.message, song_id, edit_text)


@bot.callback_query_handler(func=None, calendar_config=edit_song_callback.filter())
def edit_song_options(call: CallbackQuery):
    """Manage song edit options: Name, Sheets, Sound or DELETE"""

    _, song_id, option_id = call.data.split(":")

    # change name
    if option_id == "0":
        print(f"edit_song_options {option_id}")
        msg = bot.send_message(call.message.chat.id, song_d.enter_new_name_text)
        bot.register_next_step_handler(msg, enter_new_song_name, song_id)

    # add/delete sheets
    elif option_id == "1":
        print(f"edit_song_options {option_id}")
        sheets = db_songs.get_sheets_by_song_id(song_id)
        call_config = "edit_song_material"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for edit_id, text in enumerate(ch_d.edit_buttons_text_tuple):
            data.append((text, f"{call_config}:{song_id}:{option_id}:{edit_id}"))

        if sheets:
            for sh in sheets:
                sheets_data.append(InputMediaDocument(sh[3]))
            bot.send_media_group(call.message.chat.id, sheets_data)
            msg = song_d.add_or_delete_text

        else:
            data.pop()
            msg = song_d.not_net_text

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    # add/delete sounds
    elif option_id == "2":
        print(f"edit_song_options {option_id}")
        sounds = db_songs.get_sounds_by_song_id(song_id)
        call_config = "edit_song_material"
        data = []
        sheets_data = []

        # add/remove/close buttons
        for edit_id, text in enumerate(ch_d.edit_buttons_text_tuple):
            data.append((text, f"{call_config}:{song_id}:{option_id}:{edit_id}"))

        if sounds:
            for sound in sounds:
                sheets_data.append(InputMediaAudio(sound[3]))
            bot.send_media_group(call.message.chat.id, sheets_data)
            msg = song_d.add_or_delete_text

        else:
            data.pop()
            msg = song_d.not_sound_text

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    # delete song
    else:
        if not db_songs.song_exists(song_id):
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, song_d.song_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        item_name = db_songs.get_song_name(song_id)
        call_config = "delete_confirmation"
        item_type = "song"
        data = []
        msg = f"{ch_d.delete_confirmation_text} {item_name}?"

        for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
            data.append((answer, f"{call_config}:{item_type}:{song_id}:{i}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def enter_new_song_name(message: Message, song_id):
    """UPDATE the song name in the database"""

    print(f"enter_new_song_name {song_id}, {message.text}")
    if "/" in message.text:
        bot.send_message(message.chat.id, CANCELED)
        return

    elif db_songs.edit_song_name(song_id, message.text):
        bot.send_message(message.chat.id, song_d.song_name_changed_text)

    else:
        bot.send_message(message.chat.id, song_d.SONG_WRONG_TEXT)


@bot.callback_query_handler(func=None, calendar_config=edit_song_material_callback.filter())
def edit_song_materials(call: CallbackQuery):
    """Add or Remove sheets and sounds for a song"""

    print(f"edit_song_materials {call.data}")
    _, song_id, option_id, edit_id = call.data.split(":")

    def _add():
        msg = bot.send_message(call.message.chat.id, song_d.drop_the_file_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    def _delete():
        item_name = db_songs.get_song_name(song_id)
        if not item_name:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, song_d.song_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        if option_id == "1":
            call_config = "delete_confirmation"
            item_type = "sheets"
            data = []
            msg = f"{ch_d.delete_confirmation_text} {ch_d.all_sounds_text} {item_name}?"

        else:
            call_config = "delete_confirmation"
            item_type = "sounds"
            data = []
            msg = f"{ch_d.delete_confirmation_text} {ch_d.all_sounds_text} {item_name}?"

        for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
            data.append((answer, f"{call_config}:{item_type}:{song_id}:{i}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    if edit_id == "0":
        _add()

    elif edit_id == "1":
        _delete()

    else:
        bot.send_message(call.message.chat.id, song_d.SONG_WRONG_TEXT)


def add_sheets_or_sounds(message: Message, song_id):
    """Manage batch or a single file upload processing"""

    if message.document:        # sheets
        doc_file_id = message.document.file_id
        voice_id = message.document.file_name[-5]
        print(f"add_sheets_or_sounds voice id {voice_id} {message.document.file_name}")

        if voice_id.isdigit() and int(voice_id):
            voice_id = int(voice_id)
        else:
            voice_id = None

        print(f"add_sheets_or_sounds {doc_file_id}")
        db_songs.add_sheets(song_id, voice_id, doc_file_id)
        msg = bot.send_message(message.chat.id, song_d.sheets_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    elif message.audio:      # sounds
        audio_file_id = message.audio.file_id
        voice_id = message.audio.file_name[-5]
        print(f"add_sheets_or_sounds for sounds voice id {voice_id} {message.audio.file_name}")

        if voice_id.isdigit() and int(voice_id):
            voice_id = int(voice_id)
        else:
            voice_id = None

        print(f"add_sheets_or_sounds {audio_file_id}")
        db_songs.add_sound(song_id, voice_id, audio_file_id)
        msg = bot.send_message(message.chat.id, song_d.audio_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    else:
        edit_song_menu(message, song_id, song_d.something_else)


def edit_song_menu(message, song_id, msg):
    """Display buttons to edit song name, sheets or sounds"""
    print(f"edit_song_menu {bool(db_songs.song_exists(song_id))}")

    if not db_songs.song_exists(song_id):
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(message.chat.id, song_d.song_not_found_text)
        bot.send_sticker(message.chat.id, sticker_id)
        return

    call_config = "edit_song"
    data = []

    for i, option in enumerate(ch_d.song_options_to_edit_text_tuple):
        data.append((option, f"{call_config}:{song_id}:{i}"))

    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


