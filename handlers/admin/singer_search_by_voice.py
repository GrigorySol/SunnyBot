import inspect

from loader import bot, log
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback, voice_callback
from misc import callback_dict as cd
from misc.messages.singer_dictionary import choose_voice_text, no_singers_text
from keyboards.inline.choice_buttons import buttons_markup, search_choice_markup
from database_control.db_singer import get_all_voices, search_singers_by_voice


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    """Display available voices."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    voices = get_all_voices()
    call_config = cd.singer_voice_text
    data = []

    for _, text in voices:
        data.append({"text": text, "callback_data": f"{call_config}:{text}"})

    msg = choose_voice_text
    markup = buttons_markup(data, call.message.id)
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, singer_config=voice_callback.filter())
def show_voice(call: CallbackQuery):
    """Display buttons with the names of the singers."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    voice = call.data.split(":")[1]
    singers = search_singers_by_voice(voice)
    if not singers:
        bot.edit_message_text(
            no_singers_text, call.message.chat.id, call.message.id, reply_markup=search_choice_markup
        )
    else:
        call_config = cd.singer_display_text
        data = []

        for text, singer_id in singers:
            data.append({"text": text, "callback_data": f"{call_config}:{singer_id}"})

        msg = voice
        markup = buttons_markup(data, call.message.id)
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)
