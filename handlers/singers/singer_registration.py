from datetime import datetime
import inspect

from handlers.admin.singer_info import singer_info_markup
from loader import bot, log
from config import PASS_PHRASE, SECRET_PASS_PHRASE, VIP, VIP2, MENU_IMAGE
from telebot.types import Message, CallbackQuery
from keyboards.inline.choice_buttons import new_singer_markup
from keyboards.inline.callback_datas import register_callback
from misc.bot_speech import greetings
from misc import dicts
from database_control.db_singer import add_singer, block_user, add_admin, get_singer_id


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

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    print(f"Registration started for {message.from_user.username} "
          f"{message.from_user.first_name} {message.from_user.last_name}")

    singer_time = datetime.utcfromtimestamp(message.date).hour
    start_registration(message.from_user.username, message.from_user.id, singer_time)


def start_registration(telegram_name, telegram_id, singer_time):
    if not telegram_name:
        bot.send_message(telegram_id, f"{dicts.singers.need_telegram_name_text} @GrigorySol")
        return

    msg = f"{greetings(singer_time)}\n{dicts.singers.not_registered_text}"
    bot.send_message(telegram_id, msg, reply_markup=new_singer_markup)


@bot.callback_query_handler(func=None, singer_config=register_callback.filter())
def add_new_singer(call: CallbackQuery):
    """Ask to enter the secret pass-phrase."""

    singer = SingerRegister()
    msg_data = bot.send_message(call.message.chat.id, dicts.singers.enter_security_phrase_text)
    bot.register_next_step_handler(msg_data, security_control_step, singer)
    bot.delete_message(call.message.chat.id, call.message.id)


def security_control_step(message: Message, singer: SingerRegister):
    """Check the secret phrase and ask for a name."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

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
        bot.send_message(message.chat.id, f"{dicts.singers.bye_bye_text} @GrigorySol")
        del singer


def singer_name_step(message: Message, singer: SingerRegister):
    """Save the name and ask to enter a lastname."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    name = message.text
    if name and "/" in name:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)

    elif name.isalpha():
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        singer.name = name
        msg = bot.send_message(message.chat.id, dicts.singers.enter_your_lastname_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)

    elif name.isnumeric() or len(name) < 2:
        msg = bot.send_message(message.chat.id, dicts.singers.name_too_short_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)

    elif " " in name and name.count(" ") == 1:
        name, lastname = name.split(" ")
        singer.name = name
        singer.telegram_id = message.from_user.id
        singer.telegram_name = message.from_user.username
        # bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEUXldijsMSalTOs3O2M01uwWqKGzVoqwACGwADwDZPE329ioPLRE1qJAQ")
        if MENU_IMAGE:
            bot.send_photo(message.chat.id, MENU_IMAGE)
        bot.send_message(message.chat.id, dicts.singers.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, name, lastname)
        if singer.is_admin:
            from handlers.admin.command_rules import admin_command_rules
            admin_command_rules()
            add_admin(singer.telegram_id)
        finalize_registration(lastname, message, singer)

    else:
        msg = bot.send_message(message.chat.id, dicts.singers.name_incorrect_text)
        bot.register_next_step_handler(msg, singer_name_step, singer)


def finalize_registration(lastname, message, singer):

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    msg = f"New singer @{singer.telegram_name} " \
          f"{message.from_user.first_name} -> {singer.name} " \
          f"{message.from_user.last_name} -> {lastname} registered"
    print(msg)
    if VIP2:
        singer_id = get_singer_id(singer.telegram_id)
        markup = singer_info_markup(singer_id)
        bot.send_message(VIP2, msg, reply_markup=markup)

    del singer


def singer_lastname_step(message: Message, singer: SingerRegister):
    """Save lastname and finish registration"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.text and "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.chat.id, dicts.singers.lastname_is_digit_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)
    elif lastname.isalpha():
        singer.lastname = lastname
        print(f"all data:\n{singer.__dict__}")
        if MENU_IMAGE:
            bot.send_photo(message.chat.id, MENU_IMAGE)
        bot.send_message(message.chat.id, dicts.singers.thanks_for_register_text)
        add_singer(singer.telegram_id, singer.telegram_name, singer.name, singer.lastname)
        if singer.is_admin:
            add_admin(singer.telegram_id)
        finalize_registration(lastname, message, singer)
    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, singer_lastname_step, singer)
