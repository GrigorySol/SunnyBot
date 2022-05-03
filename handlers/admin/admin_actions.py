from loader import bot
from db import BotDB
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from keyboards.inline.choice_buttons import callback_buttons, search_choice
from misc.bot_dictionary import *

BotDB = BotDB("sunny_bot.db")


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search options"""
    is_admin = BotDB.is_admin(message.from_user.id)
    if is_admin:
        amount = BotDB.count_singers()
        bot.send_message(message.chat.id,
                         f"В хоре {amount} певунов.\n{show_singers_text}",
                         reply_markup=search_choice)
    else:
        bot.send_message(message.chat.id, you_shell_not_pass)


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""
    singers = BotDB.get_all_singers()
    call_config = "singer"
    data = []
    for singer in singers:
        data.append((singer[0], f"{call_config}:{singer[1]}"))
    bot.send_message(call.message.chat.id, show_all_singers_text,
                     reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.inline_handler(func=lambda query: len(query.query))
def singer_query(query: InlineQuery):
    """Inline User Search"""
    singers = BotDB.get_all_singers()
    call_config = "singer"
    data = []
    for i, singer in enumerate(singers):
        if query.query.lower().strip() in "".join(singer[0]).lower():
            btn = callback_buttons([(singer[0], f"{call_config}:{singer[1]}")])
            content = InputTextMessageContent(f"___________")
            data.append(InlineQueryResultArticle(i, singer[0], content, reply_markup=btn))
    bot.answer_inline_query(query.id, data)



