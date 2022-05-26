from datetime import datetime

from loader import bot
from config import PASS_PHRASE, SECRET_PASS_PHRASE, VIP
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import new_singer_markup
from keyboards.inline.callback_datas import register_callback
from misc.bot_speech import greetings
from misc import dicts
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

    print(f"Registration started for {message.from_user.username} "
          f"{message.from_user.first_name} {message.from_user.last_name}")
    if not message.from_user.username:
        bot.send_message(message.chat.id, dicts.singers.need_telegram_name_text)
        return
        
    telegram_id = message.from_user.id
    singer_time = datetime.utcfromtimestamp(message.date).hour

    if message.from_user.username == "Alex_3owls":
        text = f"{greetings(singer_time)}, Сашенька\n"
    else:
        text = f"{greetings(singer_time)}\n"
    text += dicts.singers.not_registered_text
    bot.send_message(telegram_id, text, reply_markup=new_singer_markup)


@bot.callback_query_handler(func=None, singer_config=register_callback.filter())
def add_new_singer(call: CallbackQuery):
    """Ask to enter the secret pass-phrase."""

    singer = SingerRegister()
    msg_data = bot.send_message(call.message.chat.id, dicts.singers.enter_security_phrase_text)
    bot.register_next_step_handler(msg_data, security_control_step, singer)
    bot.delete_message(call.message.chat.id, call.message.id)


def security_control_step(message: Message, singer: SingerRegister):
    """Check the secret phrase and ask for a name."""

    print(f"{message.text} from {message.from_user.username} {message.from_user.first_name}")
    if message.text and "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if message.text.lower().strip() == SECRET_PASS_PHRASE:
        singer.is_admin = True
        msg_data = bot.send_message(message.chat.id, dicts.singers.admin_welcome_text)
        bot.register_next_step_handler(msg_data, singer_name_step, singer)

    elif message.text.lower().strip() == PASS_PHRASE:
        msg_data = bot.send_message(message.chat.id, dicts.singers.enter_your_name_text)
        bot.register_next_step_handler(msg_data, singer_name_step, singer)

    elif singer.count == 7:
        msg_data = bot.send_message(message.chat.id, dicts.singers.how_many_times_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    elif singer.count > 1:
        msg_data = bot.send_message(message.chat.id, dicts.singers.wrong_security_phrase_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    elif singer.count:
        msg = f"{message.from_user.username} {dicts.singers.trying_to_register_text}\n" \
              f"{dicts.singers.right_answer_text} - {PASS_PHRASE}"
        bot.send_message(VIP, msg)
        msg_data = bot.send_message(message.chat.id, dicts.singers.one_more_attempt_text)
        bot.register_next_step_handler(msg_data, security_control_step, singer)
        singer.decrease_count()

    else:
        block_user(message.from_user.id, message.from_user.username)
        bot.send_message(message.chat.id, dicts.singers.bye_bye_text)
        del singer


def singer_name_step(message: Message, singer: SingerRegister):
    """Save the name and ask to enter a lastname."""

    print(f"{message.text} {len(message.text)}")
    name = message.text
    if name and "/" in name:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    elif name.isdigit():
        msg = bot.send_message(message.chat.id, dicts.singers.name_is_digit_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    elif " " in name and len(name) > 3:
        name, lastname = name.split(" ")
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEUXldijsMSalTOs3O2M01uwWqKGzVoqwACGwADwDZPE329ioPLRE1qJAQ")
        bot.send_message(message.chat.id, dicts.singers.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, name, lastname)
        if singer.is_admin:
            from handlers.admin.command_rules import admin_command_rules
            admin_command_rules()
            add_admin(singer.telegram_id)
        print(f"New singer {name} {lastname} registered")
        del singer

    elif len(name) < 2 or " " in name:
        msg = bot.send_message(message.chat.id, dicts.singers.name_too_short_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    else:
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        singer.name = name
        msg = bot.send_message(message.chat.id, dicts.singers.enter_your_lastname_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)


def singer_lastname_step(message: Message, singer: SingerRegister):
    """Save lastname and finish registration"""

    print(f"{message.text} {len(message.text)}")
    if message.text and "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.chat.id, dicts.singers.lastname_is_digit_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)
    else:
        singer.lastname = lastname
        print(f"all data:\n{singer.__dict__}")
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEUXldijsMSalTOs3O2M01uwWqKGzVoqwACGwADwDZPE329ioPLRE1qJAQ")
        bot.send_message(message.chat.id, dicts.singers.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, singer.name, singer.lastname)
        if singer.is_admin:
            add_admin(singer.telegram_id)
        print(f"New singer {singer.name} {singer.lastname} registered")
        del singer
