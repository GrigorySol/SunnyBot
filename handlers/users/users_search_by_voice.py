from loader import bot
from db import BotDB
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback
from misc.bot_dictionary import chose_voice_text, no_users_text
from keyboards.inline.choice_buttons import voice_choice, voices_dict, search_choice

BotDB = BotDB("sunny_bot.db")


@bot.callback_query_handler(func=None, user_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    bot.send_message(call.from_user.id, chose_voice_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=voice_choice)


def chosen_voice(call: CallbackQuery):
    for voice in voices_dict:
        if call.data == voice:
            return True
    return False


@bot.callback_query_handler(func=chosen_voice)
def bass_voice(call: CallbackQuery):
    singers = BotDB.search_users_by_voice(voices_dict[call.data])
    print(singers)
    bot.send_message(call.from_user.id, f"Вы выбрали {voices_dict[call.data]}")
    for singer in singers:
        msg = f"{singer[1]} {singer[2]} @{singer[0]}"
        if len(singer) > 3:
            msg += f" ({singer[3]})"
        bot.send_message(call.from_user.id, msg)
    if not singers:
        bot.send_message(call.from_user.id, no_users_text, reply_markup=search_choice)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
