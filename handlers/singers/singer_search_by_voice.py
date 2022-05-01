from loader import bot
from db import BotDB
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback
from misc.bot_dictionary import chose_voice_text, no_singers_text
from keyboards.inline.choice_buttons import callback_buttons, search_choice

BotDB = BotDB("sunny_bot.db")
voices = [voice[0] for voice in BotDB.get_voice_list()]


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    """Display available voices. TODO: FIX dictionary"""
    bot.send_message(call.message.chat.id, chose_voice_text, reply_markup=callback_buttons(voices))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def chosen_voice(call: CallbackQuery):
    for voice in voices:
        if call.data == voice:
            return True
    return False


@bot.callback_query_handler(func=chosen_voice)
def show_voice(call: CallbackQuery):
    """Display inline callback buttons with the name of the singers."""
    singers = BotDB.search_singers_by_voice(call.data)
    if not singers:
        bot.send_message(call.message.chat.id, no_singers_text, reply_markup=search_choice)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    else:
        msg = f"Вы выбрали {call.data}"
        call_data = "search:singer"
        data = []
        for singer in singers:
            data.append(f"{singer[1]} {singer[2]}")
        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data, call_data=call_data))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
