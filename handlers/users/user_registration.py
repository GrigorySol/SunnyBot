from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.callback_datas import register_callback
from misc.bot_dictionary import *
from db import BotDB

BotDB = BotDB("sunny_bot.db")


class UserRegister:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.name = None
        self.lastname = None


user = UserRegister()


@bot.callback_query_handler(func=None, user_config=register_callback.filter())
def add_new_user(call: CallbackQuery):
    msg = bot.send_message(call.from_user.id, enter_your_name)
    bot.register_next_step_handler(msg, user_name_step)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


def user_name_step(message: Message):
    name = message.text
    if " " in name and len(name) > 3:
        name, lastname = name.split(" ")
        user.user_id = message.from_user.id
        user.username = message.from_user.username
        bot.send_message(message.from_user.id, "Спасибо за регистрацию!")
        BotDB.add_user(user.user_id, user.username, name, lastname)
        print(f"New user {name} {lastname} registered")
    elif name.isdigit():
        msg = bot.send_message(message.from_user.id,
                               "Дразниться не обязательно!\n"
                               "Пожалуйста, напишите Ваше имя буквами.")
        bot.register_next_step_handler(msg, user_name_step)

    elif len(name) < 2 or " " in name:
        msg = bot.send_message(message.from_user.id,
                               "Вы же не R2D2?\n"
                               "Пожалуйста, напишите Ваше имя полностью %)")
        bot.register_next_step_handler(msg, user_name_step)
    else:
        user.user_id = message.from_user.id
        user.username = message.from_user.username
        user.name = name
        msg = bot.send_message(message.from_user.id,
                               "Пожалуйста, напишите Вашу фамилию (можно одной буквой).")
        bot.register_next_step_handler(msg, user_lastname_step)


def user_lastname_step(message: Message):
    lastname = message.text
    if lastname.isdigit():
        msg = bot.send_message(message.from_user.id,
                               "Цифры не подходят.\n"
                               "Пожалуйста, напишите Вашу фамилию буквами (хотя бы одной).")
        bot.register_next_step_handler(msg, user_lastname_step)
    else:
        user.lastname = lastname
        bot.send_message(message.from_user.id, "Спасибо за регистрацию!")
        BotDB.add_user(user.user_id, user.username, user.name, user.lastname)
        print(f"New user {user.name} {user.lastname} registered")
