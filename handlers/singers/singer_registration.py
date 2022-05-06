from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import register_callback
from misc.messages.singer_dictionary import enter_your_name_text, thanks_for_register_text,\
    name_too_short_text, enter_your_lastname_text, lastname_is_digit_text, name_is_digit_text
from database_control.db_singer import add_singer


class SingerRegister:
    def __init__(self):
        self.singer_id = None
        self.singername = None
        self.name = None
        self.lastname = None


singer = SingerRegister()


@bot.callback_query_handler(func=None, singer_config=register_callback.filter())
def add_new_singer(call: CallbackQuery):
    msg_data = bot.send_message(call.message.chat.id, enter_your_name_text)
    bot.register_next_step_handler(msg_data, singer_name_step)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def singer_name_step(message: Message):
    name = message.text
    if " " in name and len(name) > 3:
        name, lastname = name.split(" ")
        singer.singer_id = message.from_user.id
        singer.singername = message.from_user.username
        bot.send_message(message.chat.id, thanks_for_register_text)
        add_singer(singer.singer_id, singer.singername, name, lastname)
        print(f"New singer {name} {lastname} registered")
    elif name.isdigit():
        msg = bot.send_message(message.chat.id, name_is_digit_text)
        bot.register_next_step_handler(msg, singer_name_step)

    elif len(name) < 2 or " " in name:
        msg = bot.send_message(message.chat.id, name_too_short_text)
        bot.register_next_step_handler(msg, singer_name_step)
    else:
        singer.singer_id = message.from_user.id
        singer.singername = message.from_user.username
        singer.name = name
        msg = bot.send_message(message.chat.id, enter_your_lastname_text)
        bot.register_next_step_handler(msg, singer_lastname_step)


def singer_lastname_step(message: Message):
    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.chat.id, lastname_is_digit_text)
        bot.register_next_step_handler(msg, singer_lastname_step)
    else:
        singer.lastname = lastname
        bot.send_message(message.chat.id, thanks_for_register_text)
        add_singer(singer.singer_id, singer.singername, singer.name, singer.lastname)
        print(f"New singer {singer.name} {singer.lastname} registered")
