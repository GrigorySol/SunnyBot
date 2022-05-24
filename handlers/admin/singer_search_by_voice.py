from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import search_callback, voice_callback
from misc.messages.singer_dictionary import choose_voice_text, no_singers_text
from keyboards.inline.choice_buttons import callback_buttons, search_choice_markup
from database_control.db_singer import get_all_voices, search_singers_by_voice


@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="voice"))
def search_by_voice(call: CallbackQuery):
    """Display available voices."""
    print(f"search_by_voice {call.data}")
    voices = get_all_voices()
    call_config = "voice"
    data = []
    for _, voice in voices:
        data.append((voice, f"{call_config}:{voice}"))
    bot.edit_message_text(
        choose_voice_text, call.message.chat.id, call.message.id, reply_markup=callback_buttons(data, row=3)
    )


@bot.callback_query_handler(func=None, singer_config=voice_callback.filter())
def show_voice(call: CallbackQuery):
    """Display inline callback buttons with the name of the singers."""
    print(f"show_voice {call.data}")
    voice = call.data.split(":")[1]
    singers = search_singers_by_voice(voice)
    if not singers:
        bot.edit_message_text(
            no_singers_text, call.message.chat.id, call.message.id, reply_markup=search_choice_markup
        )
    else:
        msg = f"Вы выбрали {voice}"
        call_config = "show_singer"
        data = []
        for name, singer_id in singers:
            data.append((name, f"{call_config}:{singer_id}"))
        bot.edit_message_text(
            msg, call.message.chat.id, call.message.id, reply_markup=callback_buttons(data)
        )
