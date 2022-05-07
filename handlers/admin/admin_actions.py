from loader import bot
from datetime import date
from telebot.types import Message, CallbackQuery, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from keyboards.inline.choice_buttons import callback_buttons, search_choice_markup, query_button
from keyboards.inline.calendar_buttons import generate_calendar_days
from keyboards.inline.callback_datas import add_new_callback
from misc.messages.singer_dictionary import show_singers_text, you_shell_not_pass_text, show_all_singers_text, NOTHING
from misc.messages.event_dictionary import set_event_date_text
from database_control import db_singer


@bot.message_handler(commands=["singers"])
def show_singers_search(message: Message):
    """Display callback buttons with search options"""
    is_admin = db_singer.is_admin(message.from_user.id)
    if is_admin:
        amount = db_singer.count_singers()
        bot.send_message(message.chat.id, f"В хоре {amount} певунов.\n{show_singers_text}",
                         reply_markup=search_choice_markup)
    else:
        bot.send_message(message.chat.id, you_shell_not_pass_text)


"""
@bot.message_handler(commands=["add"])
def add_command(message: Message):
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAETnWpicItgGPH0dCO0X4bH2qcWNQIHUgAC6hYAAq5s6EltZQABkuvO0TUkBA")
"""


@bot.callback_query_handler(func=lambda c: c.data == "show_all")
def show_all_singers(call: CallbackQuery):
    """Displays callback buttons with all singers"""
    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []
    for singer in singers:
        data.append((singer[0], f"{call_config}:{singer[1]}"))
    bot.send_message(call.message.chat.id, show_all_singers_text, reply_markup=callback_buttons(data))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.inline_handler(func=lambda query: len(query.query))
def location_query(query: InlineQuery):
    """Inline User Search"""
    singers = db_singer.get_all_singers()
    call_config = "show_singer"
    data = []
    for i, singer in enumerate(singers):
        if query.query.lower().strip() in singer[0].lower():
            voices = ", ".join([voice for _, voice in db_singer.get_singer_voices(singer[1])])
            suits = ", ".join([suit for _, suit, _ in db_singer.get_singer_suits(singer[1])])
            if voices and suits:
                content = InputTextMessageContent(f"| Голос: {voices}\n| Костюмы: {suits}")
            elif voices:
                content = InputTextMessageContent(f"| Голос: {voices}")
            elif suits:
                content = InputTextMessageContent(f"| Костюмы: {suits}")
            else:
                content = InputTextMessageContent(f"| У этого певуна ещё нет ни голоса, ни костюмов.")
            btn = query_button(singer[0], f"{call_config}:{singer[1]}")
            data.append(InlineQueryResultArticle(i, singer[0], content, reply_markup=btn))
    bot.answer_inline_query(query.id, data)


@bot.callback_query_handler(func=None, calendar_config=add_new_callback.filter())
def song_or_event(call: CallbackQuery):
    """Get id from data and call a song or an event creation"""
    print(f"song_or_event {call.data}")
    _, _id = call.data.split(":")
    if _id == "4":
        print(f"ADD NEW SONG routing")
        # TODO: Create logic
        bot.send_message(call.message.chat.id, NOTHING)
    else:
        """Show calendar buttons"""
        now = date.today()
        bot.send_message(call.message.chat.id, set_event_date_text,
                         reply_markup=generate_calendar_days(now.year, now.month, int(_id)))
