from loader import bot
from db import BotDB
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback, voice_callback
from misc.bot_dictionary import chose_voice_text, no_singers_text
from keyboards.inline.choice_buttons import callback_buttons, search_choice

BotDB = BotDB("sunny_bot.db")


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    """Display available voices."""
    print("here")
    voices = BotDB.get_voice_list()
    call_config = "voice"
    data = []
    for voice in voices:
        data.append((voice[0], f"{call_config}:{voice[0]}"))
    bot.send_message(call.message.chat.id, chose_voice_text, reply_markup=callback_buttons(data, row=3))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=None, singer_config=voice_callback.filter())
def show_voice(call: CallbackQuery):
    """Display inline callback buttons with the name of the singers."""
    voice = call.data.split(":")[1]
    singers = BotDB.search_singers_by_voice(voice)
    if not singers:
        bot.send_message(call.message.chat.id, no_singers_text, reply_markup=search_choice)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    else:
        msg = f"Вы выбрали {voice}"
        call_config = "singer"
        data = []
        for singer in singers:
            data.append((singer[0], f"{call_config}:{singer[1]}"))
        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
