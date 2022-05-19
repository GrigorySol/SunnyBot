from datetime import datetime

from loader import bot
from config import PASS_PHRASE, SECRET_PASS_PHRASE, VIP
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import new_singer_markup
from keyboards.inline.callback_datas import register_callback
from misc.bot_speech import greetings
from misc.messages import singer_dictionary as sin_d
from database_control.db_singer import add_singer, block_user, add_admin


class SingerRegister:
    def __init__(self):
        self.telegram_id = None
        self.telegram_name = None
        self.name = None
        self.lastname = None
        self.is_admin = False
        self.count = 10

    def decrease_count(self):
        self.count -= 1


@bot.message_handler(is_blocked=True)
def user_blocked(message: Message):
    """Ignore blocked user"""
    print(f"User_id = {message.from_user.id} and telegram name is {message.from_user.username}")


@bot.message_handler(is_new_singer=True)
def singer_not_registered(message: Message):
    """Interact with a new user and offer to register"""

    telegram_id = message.from_user.id
    singer_time = datetime.utcfromtimestamp(message.date).hour

    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(singer_time)}, Сашенька\n"
    else:
        text = f"{greetings(singer_time)}\n"
    text += sin_d.not_registered_text
    bot.send_message(telegram_id, text, reply_markup=new_singer_markup)


@bot.callback_query_handler(func=None, singer_config=register_callback.filter())
def add_new_singer(call: CallbackQuery):
    """Ask to enter the secret pass-phrase."""

    singer = SingerRegister()
    msg_data = bot.send_message(call.message.chat.id, sin_d.enter_security_phrase_text)
    bot.register_next_step_handler(msg_data, security_control_step, singer)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def security_control_step(message: Message, singer: SingerRegister):
    """Check the secret phrase and ask for a name."""

    if message.text == SECRET_PASS_PHRASE:
        singer.is_admin = True
        msg_data = bot.send_message(message.chat.id, sin_d.admin_welcome_text)
        bot.register_next_step_handler(msg_data, singer_name_step, singer)

    elif message.text == PASS_PHRASE:
        msg_data = bot.send_message(message.chat.id, sin_d.enter_your_name_text)
        bot.register_next_step_handler(msg_data, singer_name_step, singer)

    elif singer.count == 7:
        msg_data = bot.send_message(message.chat.id, sin_d.how_many_times_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    elif singer.count > 1:
        msg_data = bot.send_message(message.chat.id, sin_d.wrong_security_phrase_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    elif singer.count:
        msg = f"{message.from_user.username} {sin_d.trying_to_register_text}\n" \
              f"{sin_d.right_answer_text} - {PASS_PHRASE}"
        bot.send_message(VIP, msg)
        msg_data = bot.send_message(message.chat.id, sin_d.one_more_attempt_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    else:
        block_user(message.from_user.id, message.from_user.username)
        bot.send_message(message.chat.id, sin_d.bye_bye_text)
        del singer


def singer_name_step(message: Message, singer: SingerRegister):
    """Save the name and ask to enter a lastname."""

    name = message.text
    if "/" in name:
        msg = bot.send_message(message.chat.id, sin_d.name_is_a_command_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    elif name.isdigit():
        msg = bot.send_message(message.chat.id, sin_d.name_is_digit_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    elif " " in name and len(name) > 3:
        name, lastname = name.split(" ")
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        bot.send_message(message.chat.id, sin_d.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, name, lastname)
        if singer.is_admin:
            add_admin(singer.telegram_id)
        print(f"New singer {name} {lastname} registered")
        del singer

    elif len(name) < 2 or " " in name:
        msg = bot.send_message(message.chat.id, sin_d.name_too_short_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    else:
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        singer.name = name
        msg = bot.send_message(message.chat.id, sin_d.enter_your_lastname_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)


def singer_lastname_step(message: Message, singer: SingerRegister):
    """Save lastname and finish registration"""

    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.chat.id, sin_d.lastname_is_digit_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)
    else:
        singer.lastname = lastname
        bot.send_message(message.chat.id, sin_d.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, singer.name, singer.lastname)
        if singer.is_admin:
            add_admin(singer.telegram_id)
        print(f"New singer {singer.name} {singer.lastname} registered")
        del singer
