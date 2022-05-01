from loader import bot
from db import BotDB
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback
from misc.bot_dictionary import chose_voice_text, no_singers_text
from keyboards.inline.choice_buttons import voice_choice, voices_dict, search_choice, naming_buttons

BotDB = BotDB("sunny_bot.db")


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    bot.send_message(call.message.chat.id, chose_voice_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=voice_choice)


def chosen_voice(call: CallbackQuery):
    for voice in voices_dict:
        if call.data == voice:
            return True
    return False


@bot.callback_query_handler(func=chosen_voice)
def bass_voice(call: CallbackQuery):
    singers = BotDB.search_singers_by_voice(voices_dict[call.data])
    print(singers)
    if not singers:
        bot.send_message(call.message.chat.id, no_singers_text, reply_markup=search_choice)
    else:
        msg = f"Вы выбрали {voices_dict[call.data]}"
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
        bot.send_message(call.message.chat.id, msg, reply_markup=naming_buttons(singers))
