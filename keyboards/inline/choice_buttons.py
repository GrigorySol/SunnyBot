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
search_choice_markup = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton("По имени", switch_inline_query_current_chat="а")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")
show_all_btn = InlineKeyboardButton("Посмотреть всех", callback_data="show_all")
search_choice_markup.add(search_by_name, search_by_voice, show_all_btn)
search_choice_markup.add(close_btn)

# Reply with joke
accept_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes_btn = KeyboardButton("Да!")
of_course_btn = KeyboardButton("Конечно!")
accept_markup.add(yes_btn, of_course_btn, close_btn)

# choose old or new location buttons
choose_location_markup = InlineKeyboardMarkup(row_width=2)
choose_old = InlineKeyboardButton("Выбрать", callback_data="location:db")
get_url = InlineKeyboardButton("Добавить", callback_data="location:url")
choose_location_markup.add(choose_old, get_url)
choose_location_markup.add(close_btn)


def add_concert_songs_buttons(concert_id):
    concert_markup = InlineKeyboardMarkup(row_width=1)
    add_songs_button = InlineKeyboardButton("Добавить песни в программу", callback_data=f"change_songs:{concert_id}:0")
    concert_markup.add(add_songs_button)
    concert_markup.add(close_btn)
    return concert_markup


def repeat_buttons(eid):
    repeat_markup = InlineKeyboardMarkup(row_width=1)
    repeat_button = InlineKeyboardButton("Повторить", callback_data=f"repeat:{eid}")
    repeat_markup.add(repeat_button)
    repeat_markup.add(close_btn)
    return repeat_markup


def change_buttons(name, _id):
    change_markup = InlineKeyboardMarkup(row_width=1)
    attend_button = InlineKeyboardButton("Посещение", callback_data=f"show_attendance:{_id}")
    change_button = InlineKeyboardButton("Изменить", callback_data=f"change:{name}:{_id}")
    change_markup.add(attend_button)
    change_markup.add(change_button)
    change_markup.add(close_btn)
    return change_markup


def query_button(text, call_data):
    query_markup = InlineKeyboardMarkup()
    query_btn = InlineKeyboardButton(text, callback_data=call_data)
    query_markup.add(query_btn)
    return query_markup


def callback_buttons(data: List, row=2):
    """
    Create group of the buttons.
    data: [(text, callback_data)]
    """
    markup = InlineKeyboardMarkup(row_width=row)
    buttons = [
        InlineKeyboardButton(text[0], callback_data=text[1])
        for text in data
    ]
    markup.add(*buttons)
    markup.add(close_btn)
    return markup


def singer_info_buttons(telegram_name, sid, btn_names):
    print(f"{telegram_name}, {sid}, {btn_names}")
    markup = InlineKeyboardMarkup(row_width=2)
    send_msg_btn = InlineKeyboardButton("Написать", url=f"t.me/{telegram_name}")
    buttons = [send_msg_btn]
    for name in btn_names:
        btn = InlineKeyboardButton(name, callback_data=f"info:{name}:{sid}")
        buttons.append(btn)
    markup.add(*buttons)
    markup.add(close_btn)
    return markup


def message_buttons(data: List, row=2):
    markup = InlineKeyboardMarkup(row_width=row)
    buttons = [
        InlineKeyboardButton(f"{fullname} {attendance}", url=f"t.me/{telegram_name}")
        for fullname, telegram_name, attendance in data
    ]
    markup.add(*buttons)
    markup.add(close_btn)
    return markup
