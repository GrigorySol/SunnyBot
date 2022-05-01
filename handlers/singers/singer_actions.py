from datetime import datetime
from loader import bot
from db import BotDB
from telebot.types import Message, CallbackQuery, InlineQuery, \
    InlineQueryResultArticle, InputTextMessageContent
from keyboards.inline.choice_buttons import new_singer_markup, search_choice
from keyboards.inline.callback_datas import search_callback
from misc.bot_speech import greetings, random_answer
from misc.bot_dictionary import *

BotDB = BotDB("sunny_bot.db")


# If the singer is not in the database
@bot.message_handler(is_new_singer=True)
def singer_not_registered(message: Message):
    singer_id = message.from_user.id
    singer_time = datetime.utcfromtimestamp(message.date).hour
    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(singer_time)}, Сашенька\n"
    else:
        text = f"{greetings(singer_time)}\n"
    text += not_registered_text
    bot.send_message(singer_id, text, reply_markup=new_singer_markup)


@bot.message_handler(commands=["singers"])
def show_singers(message: Message):
    amount = BotDB.count_singers()
    bot.send_message(message.chat.id,
                     f"В хоре {amount} певунов.\n{show_singers_text}",
                     reply_markup=search_choice)


@bot.message_handler(commands=["voice"])
def show_by_voice(message: Message):
    voice = BotDB.search_singer_voice(message.from_user.id)[0][0]
    if not voice:
        bot.send_message(message.chat.id, no_voice_text)
    bot.send_message(message.chat.id, f"Вы поёте в {voice}.")


"""
@bot.callback_query_handler(func=None, singer_config=search_callback.filter(type="singer_name"))
def search_by_singer_name(call: CallbackQuery):
    bot.send_message(call.message.chat.id, enter_name_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    bot.send_message(call.message.chat.id, show_all_singers_text)
    singers = BotDB.show_singers()
    for singer in singers:
        msg = f"{singer[1]} {singer[2]} @{singer[0]} ({singer[3]})"
        bot.send_message(call.message.chat.id, msg)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'cancel')
def cancel_btn(call: CallbackQuery):
    bot.send_message(call.message.chat.id, cancel_btn_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    bot.send_message(call.message.chat.id, back_btn_text)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.inline_handler(func=lambda query: len(query.query))
def singer_query(query: InlineQuery):
    """Inline User Search"""
    singers = BotDB.show_singers()
    result = []
    for i, singer in enumerate(singers):
        if query.query.lower().strip() in "".join(singer).lower():
            print(singer)
            result.append(InlineQueryResultArticle(i, f"{singer[1]} {singer[2]} ({singer[3]})",
                                                   InputTextMessageContent(f"{singer[1]} {singer[2]} "
                                                                           f"@{singer[0]} ({singer[3]})")))
    bot.answer_inline_query(query.id, result)


# If nothing to say
@bot.message_handler()
def nothing_to_say(message: Message):
    """Random answer"""
    text = {random_answer()}  # \n\n{nothing_to_say_text}
    print(message.text)
    print(text)
    bot.send_message(message.chat.id, text)
