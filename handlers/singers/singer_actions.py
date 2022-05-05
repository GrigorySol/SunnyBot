from datetime import datetime
from random import randint
from loader import bot
import db
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.inline.callback_datas import suit_callback
from keyboards.inline.choice_buttons import new_singer_markup, joke_markup, callback_buttons
from misc.bot_speech import greetings
from misc.bot_dictionary import *


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


@bot.message_handler(commands=["voice"])
def show_voice(message: Message):
    """Display singer voices"""
    singer_id = db.get_singer_id(message.from_user.id)
    voices = db.get_singer_voices(singer_id)
    if not voices:
        bot.send_message(message.chat.id, no_voice_text)
    else:
        bot.send_message(message.chat.id, f"Вы поёте в {voices}.")


@bot.message_handler(commands=["suits"])
def show_suits(message: Message):
    """Display singer suits and buttons to add or remove"""
    sid = db.get_singer_id(message.from_user.id)
    suits = db.get_singer_suits(sid)
    call_config = "suit"
    data = []

    for text in edit_buttons:
        data.append((text, f"{call_config}:{text}:{sid}"))

    if not suits:
        data.pop()
        msg = f"{no_suit_text} {edit_suit_text}"

    elif len(db.get_all_suits()) == len(suits):
        data.pop(0)
        suit_names = []
        for _, name, photo in suits:
            suit_names.append(name)
            bot.send_photo(message.chat.id, photo, caption=name)
            bot.send_message(message.chat.id, "_____________________________")

        msg = f"Вы носите {', '.join(suit_names)}.\n{too_many_suits}\n{edit_suit_text}"

    else:
        suit_names = []
        for _, name, photo in suits:
            suit_names.append(name)
            bot.send_photo(message.chat.id, photo, caption=name)
            bot.send_message(message.chat.id, "_____________________________")

        msg = f"Вы носите {', '.join(suit_names)}.\n{edit_suit_text}"
    bot.send_message(message.chat.id, msg, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=None, singer_config=suit_callback.filter())
def display_suits_to_add_or_remove(call: CallbackQuery):
    """Display suits to add or remove"""
    _, action, sid = call.data.split(":")
    sid = int(sid)
    call_config, msg = action_definition(action)
    data = []

    if action == "Удалить":
        suits = db.get_singer_suits(sid)
        for suit_id, name, _ in suits:
            data.append((name, f"{call_config}:suit:{sid}:{suit_id}"))
    else:
        suits = db.get_all_suits()
        bot.send_message(call.message.chat.id, "_____________________________")
        for suit_id, name, photo in suits:
            available = db.get_singer_suits(sid)
            if (suit_id, name, photo) in available:
                continue
            data.append((name, f"{call_config}:suit:{sid}:{suit_id}"))
            bot.send_photo(call.message.chat.id, photo, caption=name)
            bot.send_message(call.message.chat.id, "_____________________________")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
    bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))


@bot.callback_query_handler(func=lambda c: c.data == 'close')
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)


@bot.message_handler(func=lambda m: "скучно" in m.text.lower())
def back_btn(message: Message):
    """Send a random joke into the chat"""
    bot.register_next_step_handler(message, joking)
    bot.send_message(message.chat.id, do_you_wanna_my_joke,
                     reply_to_message_id=message.id, reply_markup=joke_markup)


def joking(message: Message):
    msg = randomizer(random_jokes)
    bot.send_message(message.chat.id, msg, reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda c: c.data == 'back')
def back_btn(call: CallbackQuery):
    pass


def check_commands(message: Message):
    if message.text[0] == "/":
        return
    return message


@bot.message_handler(func=check_commands)
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""
    text = {randomizer(random_answer_text)}
    bot.forward_message(434767263, message.chat.id, message.id)
    print(message.text)
    print(text)
    bot.send_message(message.chat.id, text)


def action_definition(action: str):
    """Define what choice made by singer"""
    if action == "Удалить":
        call_config = "remove"
        msg = "Что удалить?"
    else:  # "Добавить"
        call_config = "add"
        msg = "Что дбавить?"
    return call_config, msg


def randomizer(items):
    """Takes items and returns a random item"""
    i = randint(0, len(items) - 1)
    return items[i]


@bot.message_handler(commands=["songs"])
def nothing_to_say(message: Message):
    bot.send_sticker(message.chat.id,
                     "CAACAgIAAxkBAAETnXdicIwl2s99ubWEC2ceCBR8Mk0k8QAC6hYAAgMlCEk0f7XAYR1wmiQE")


@bot.message_handler(commands=["events"])
def nothing_to_say(message: Message):
    bot.send_sticker(message.chat.id,
                     "CAACAgIAAxkBAAETnXxicIxNf0TYCRSrmzD9SD-iTjSr1QAClBQAAsBCeEsVRtvoCLXI0iQE")


@bot.message_handler(commands=["rehearsal"])
def nothing_to_say(message: Message):
    bot.send_sticker(message.chat.id,
                     "CAACAgIAAxkBAAETnX5icIyDshGmTfhQFatW5TJnbJkjkQACtBoAApsZwUq8_BZS0faNxyQE")


@bot.message_handler(commands=["concerts"])
def nothing_to_say(message: Message):
    bot.send_audio(message.chat.id,
                   "CQACAgIAAxkBAAETnYJicIzUt04joDIy7_uLOkUpHENW3wACKBoAAhFE4UpblvEevwxe_yQE")


"""
@bot.callback_query_handler(func=None)
def remove_btn(call: CallbackQuery):
    # Close unused buttons
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)
"""
