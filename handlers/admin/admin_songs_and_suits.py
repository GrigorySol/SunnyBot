import datetime
import inspect

from config import VIP
from loader import bot, log
from telebot.types import Message, CallbackQuery, InputMediaAudio, InputMediaDocument
from database_control import db_songs, db_singer
from misc import dicts, keys, tools
from misc.dictionaries import callback_dictionary as cd


@bot.callback_query_handler(func=None, singer_config=keys.call.display_suit_buttons_callback.filter())
def display_buttons_of_suits(call: CallbackQuery):
    """Display suit buttons to choose"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    suits = db_singer.get_all_suits()
    call_config = f"{dicts.call_dic.change_item_text}:suit"
    msg = dicts.changes.choose_suit_text
    data = tools.generate_simple_items_data(call_config, suits)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=keys.buttons.buttons_markup(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.change_callback.filter(type="suit"))
def suit_options(call: CallbackQuery):
    """Display suit description and options to edit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    *_, item_id = call.data.split(":")

    suit = db_singer.search_suit_by_id(item_id)
    if not suit:
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, dicts.changes.suit_not_found_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    call_config = cd.selected_suit_text
    options = dicts.changes.edit_suit_text_tuple
    suit_owners = '\n'.join([name for _, name in db_singer.get_suit_owners(item_id)])
    not_owners = '\n'.join([name for _, name in db_singer.get_not_suit_owners(item_id)])
    msg = f"🥋 {suit[0]}" \
          f"\n\n{dicts.singers.owned_suit_text}\n{suit_owners}" \
          f"\n\n{dicts.singers.not_owned_suit_text}\n{not_owners}"

    bot.send_photo(call.message.chat.id, suit[1], reply_markup=keys.buttons.close_markup)
    bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.close_markup)
    tools.create_option_buttons(call.message, call_config, item_id, options)


@bot.callback_query_handler(func=None, calendar_config=keys.call.song_info_callback.filter())
def show_song_info(call: CallbackQuery):
    """
    Show song info and allow admin to edit.
    """

    song_id = call.data.split(":")[1]
    song_name = db_songs.get_song_name(song_id)
    sheets = db_songs.get_sheets_by_song_id(song_id)
    sounds = db_songs.get_sound_by_song_id(song_id)
    comment = db_songs.get_song_comment(song_id)
    media_sheets = []
    media_sounds = []
    telegram_id = call.from_user.id

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t{song_name}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    if not db_singer.singer_exists(telegram_id):
        from handlers.singers.singer_registration import start_registration
        start_registration(call.from_user.username, call.from_user.id, datetime.datetime.now().hour)
        return

    is_admin = db_singer.is_admin(telegram_id)
    singer_id = db_singer.get_singer_id(telegram_id)
    singer_voices = db_singer.get_singer_voice_id(singer_id)

    msg = f"🧾 {song_name}"

    if sheets:
        for _, _, sheet_voice_id, sheet_id in sheets:
            if not sheet_voice_id:
                media_sheets.append(InputMediaDocument(sheet_id))
                continue
            if (sheet_voice_id,) in singer_voices or is_admin:
                media_sheets.append(InputMediaDocument(sheet_id))
        if media_sheets:
            bot.send_media_group(telegram_id, media_sheets)

    else:
        msg += f"\n🎼 {dicts.songs.no_sheets_text}"

    if sounds:
        for _, _, sound_voice_id, sound_id in sounds:
            if not sound_voice_id:
                media_sounds.append(InputMediaAudio(sound_id))
                continue
            if (sound_voice_id,) in singer_voices or is_admin:
                media_sounds.append(InputMediaAudio(sound_id))
        if media_sounds:
            bot.send_media_group(telegram_id, media_sounds)
    else:
        msg += f"\n🎹 {dicts.songs.no_sounds_text}"

    if comment:
        msg += f"\n📝 {comment}"

    bot.send_message(telegram_id, msg)

    if call.message:
        if is_admin:
            msg = f"{dicts.buttons.admin_buttons_text}\n{dicts.changes.edit_text}"
            edit_song_menu(call.message, song_id, msg)


@bot.callback_query_handler(func=None, calendar_config=keys.call.edit_song_callback.filter())
def edit_song_options(call: CallbackQuery):
    """Manage song edit options: Name, Sheets, Sound or DELETE"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, song_id, option_id = call.data.split(":")

    # change name
    if option_id == "0":
        msg = bot.send_message(call.message.chat.id, dicts.songs.enter_new_name_text)
        bot.register_next_step_handler(msg, enter_new_song_name, song_id)

    # add/delete sheets
    elif option_id == "1":
        sheets = db_songs.get_sheets_by_song_id(song_id)
        call_config = cd.edit_song_material_text
        data = [
            {"text": text, "callback_data": f"{call_config}:{song_id}:{option_id}:{edit_id}"}
            for edit_id, text in enumerate(dicts.changes.add_remove_text_tuple)
        ]

        if sheets:
            msg = dicts.songs.add_or_delete_text

        else:
            data.pop()
            msg = f"{dicts.songs.no_sheets_text}\n{dicts.songs.wanna_add_text}"

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))

    # add/delete sounds
    elif option_id == "2":
        sounds = db_songs.get_sound_by_song_id(song_id)
        call_config = cd.edit_song_material_text
        data = [
            {"text": text, "callback_data": f"{call_config}:{song_id}:{option_id}:{edit_id}"}
            for edit_id, text in enumerate(dicts.changes.add_remove_text_tuple)
        ]

        if sounds:
            msg = dicts.songs.add_or_delete_text

        else:
            data.pop()
            msg = dicts.songs.not_sound_add_text

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))

    # change comment
    elif option_id == "3":
        comment = db_songs.get_song_comment(song_id)
        if comment:
            bot.send_message(call.message.chat.id, comment)
        msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_comment_text)
        bot.register_next_step_handler(msg, enter_new_song_comment, song_id)

    # delete song
    else:
        if not db_songs.song_exists(song_id):
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, dicts.songs.song_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        item_name = db_songs.get_song_name(song_id)
        call_config = cd.delete_confirmation_text
        item_type = "song"
        data = []
        msg = f"{dicts.changes.delete_confirmation_text} {item_name}?"

        for i, text in enumerate(dicts.changes.delete_confirmation_text_tuple):
            data.append({"text": text, "callback_data": f"{call_config}:{item_type}:{song_id}:{i}"})

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))

    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_song_name(message: Message, song_id):
    """UPDATE the song name in the database"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    elif db_songs.edit_song_name(song_id, message.text):
        bot.send_message(message.chat.id, dicts.songs.song_name_changed_text)

    else:
        bot.send_message(message.chat.id, dicts.songs.WRONG_TEXT)


def enter_new_song_comment(message: Message, song_id):
    """Update the comment for a song"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if db_songs.edit_song_comment(song_id, message.text):
        edit_song_menu(message, song_id, dicts.changes.comment_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_song_comment, song_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {song_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, calendar_config=keys.call.edit_song_material_callback.filter())
def edit_song_materials(call: CallbackQuery):
    """Add or Remove sheets and sounds for a song"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, song_id, option_id, edit_id = call.data.split(":")

    def _add():
        msg = bot.send_message(call.message.chat.id, dicts.songs.drop_the_file_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, int(song_id))

    def _delete():
        item_name = db_songs.get_song_name(int(song_id))
        if not item_name:
            sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
            bot.send_message(call.message.chat.id, dicts.songs.song_not_found_text)
            bot.send_sticker(call.message.chat.id, sticker_id)
            return

        if option_id == "1":
            call_config = cd.delete_confirmation_text
            item_type = "sheets"
            data = []
            msg = f"{dicts.changes.delete_confirmation_text} {dicts.changes.all_sheets_text} {item_name}?"

        else:
            call_config = cd.delete_confirmation_text
            item_type = "sounds"
            data = []
            msg = f"{dicts.changes.delete_confirmation_text} {dicts.changes.all_sounds_text} {item_name}?"

        for i, text in enumerate(dicts.changes.delete_confirmation_text_tuple):
            data.append({"text": text, "callback_data": f"{call_config}:{item_type}:{song_id}:{i}"})

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))

    if edit_id == "0":
        _add()

    elif edit_id == "1":
        _delete()

    else:
        bot.send_message(call.message.chat.id, dicts.songs.WRONG_TEXT)

    bot.delete_message(call.message.chat.id, call.message.id)


def add_sheets_or_sounds(message: Message, song_id):
    """Manage batch or a single file upload processing"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.document:        # sheets
        doc_file_id = message.document.file_id
        voice_id = voice_detect(message.document.file_name)
        db_songs.add_sheets(song_id, voice_id, doc_file_id)
        msg = bot.send_message(message.chat.id, dicts.songs.sheets_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    elif message.audio:      # sounds
        audio_file_id = message.audio.file_id
        voice_id = voice_detect(message.audio.file_name)
        db_songs.add_sound(song_id, voice_id, audio_file_id)
        msg = bot.send_message(message.chat.id, dicts.songs.audio_added_text)
        bot.register_next_step_handler(msg, add_sheets_or_sounds, song_id)

    else:
        edit_song_menu(message, song_id, dicts.singers.CANCELED)


def voice_detect(file_name):
    for i, voice in enumerate(dicts.songs.song_voices_text_tuple):
        if voice in file_name:
            print(f"{voice} in {file_name}")
            return i + 1
    return None


def edit_song_menu(message, song_id, msg):
    """Display buttons to edit song name, sheets or sounds"""

    if not db_songs.song_exists(song_id):
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(message.chat.id, dicts.songs.song_not_found_text)
        bot.send_sticker(message.chat.id, sticker_id)
        return

    call_config = cd.edit_song_text
    data = []

    for i, text in enumerate(dicts.changes.edit_song_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{song_id}:{i}"})

    bot.send_message(message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))
