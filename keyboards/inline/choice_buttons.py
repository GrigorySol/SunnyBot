from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List

# Regular buttons
confirm_btn = InlineKeyboardButton("Да", callback_data="confirm")
decline_btn = InlineKeyboardButton("Нет", callback_data="decline")
close_btn = InlineKeyboardButton("Закрыть", callback_data="close")
back_btn = InlineKeyboardButton("Вернуться в меню", callback_data="back")

# Confirmation buttons
confirm_markup = InlineKeyboardMarkup(row_width=2)
confirm_markup.add(confirm_btn)
confirm_markup.add(decline_btn)

# New singer buttons
new_singer_markup = InlineKeyboardMarkup(row_width=2)
add_singer = InlineKeyboardButton("Зарегистрироваться", callback_data="registration")
new_singer_markup.add(add_singer)
new_singer_markup.add(close_btn)

# Singer search choice buttons
search_choice = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton("По имени", switch_inline_query_current_chat="а")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")
show_all_btn = InlineKeyboardButton("Посмотреть всех", callback_data="show_all")
search_choice.add(search_by_name, search_by_voice, show_all_btn)
search_choice.add(close_btn)

# Reply with joke
joke_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes_btn = KeyboardButton("Да!")
of_course_btn = KeyboardButton("Конечно!")
joke_markup.add(yes_btn, of_course_btn)


def callback_buttons(data: List, row=2):
    """
    Create group of the buttons.
    data: [(text, callback_data)]
    """
    markup = InlineKeyboardMarkup(row_width=row)
    buttons = []
    for text in data:
        btn = InlineKeyboardButton(text[0], callback_data=text[1])
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def singer_info_buttons(singername, sid, btn_names):
    print(f"{singername}, {sid}, {btn_names}")
    markup = InlineKeyboardMarkup(row_width=2)
    send_msg_btn = InlineKeyboardButton("Написать", url=f"t.me/{singername}")
    buttons = [send_msg_btn]
    for name in btn_names:
        btn = InlineKeyboardButton(name, callback_data=f"info:{name}:{sid}")
        buttons.append(btn)
    markup.add(*buttons)
    markup.add(close_btn)
    return markup
