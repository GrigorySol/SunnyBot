from datetime import datetime
from loader import bot
from db import BotDB
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from keyboards.inline.choice_buttons import callback_buttons, new_singer_markup, search_choice
from misc.bot_speech import greetings, random_answer
from misc.bot_dictionary import *

BotDB = BotDB("sunny_bot.db")


@bot.message_handler(is_new_singer=True)
def singer_not_registered(message: Message):
    """Interact with a new user and offer to register"""
    singer_id = message.from_user.id
    singer_time = datetime.utcfromtimestamp(message.date).hour
    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(singer_time)}, Сашенька\n"
    else:
        text = f"{greetings(singer_time)}\n"
    text += not_registered_text
    bot.send_message(singer_id, text, reply_markup=new_singer_markup)


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search options"""
    amount = BotDB.count_singers()
    bot.send_message(message.chat.id,
                     f"В хоре {amount} певунов.\n{show_singers_text}",
                     reply_markup=search_choice)


@bot.message_handler(commands=["voice"])
def show_voice(message: Message):
    """TODO: Display callback buttons with voice"""
    voice = BotDB.search_singer_voice(message.from_user.id)[0][0]
    if not voice:
        bot.send_message(message.chat.id, no_voice_text)
    bot.send_message(message.chat.id, f"Вы поёте в {voice}.")


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""
    singers = BotDB.show_singers()
    call_data = "search:singer"
    data = []
    for singer in singers:
        data.append(f"{singer[1]} {singer[2]}")
    bot.send_message(call.message.chat.id, show_all_singers_text,
                     reply_markup=callback_buttons(data, call_data=call_data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'close')
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    pass


@bot.inline_handler(func=lambda query: len(query.query))
def singer_query(query: InlineQuery):
    """Inline User Search"""
    singers = BotDB.show_singers()
    call_data = "search:singer"
    result = []
    for i, singer in enumerate(singers):
        if query.query.lower().strip() in "".join(singer).lower():
            print(singer)
            result.append(InlineQueryResultArticle(i, f"{singer[1]} {singer[2]} ({singer[3]})",
                                                   InputTextMessageContent(f"Поёт в {singer[3]}"),
                                                   reply_markup=callback_buttons([f"{singer[1]} {singer[2]}"],
                                                                                 call_data=call_data)))
    bot.answer_inline_query(query.id, result)


@bot.message_handler()
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""
    text = {random_answer()}
    print(message.text)
    print(text)
    bot.send_message(message.chat.id, text)


"""
@bot.callback_query_handler(func=None)
def back_btn(call: CallbackQuery):
    # Close unused buttons
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""
