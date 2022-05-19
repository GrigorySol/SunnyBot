from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from misc.messages.event_dictionary import next_button_text, prev_button_text

EMTPY_FIELD = 'calendar_button'


class DataKeeper:
    def __init__(self):
        self.data = None
        self.row = None
        self.row_height = 5
        self.division = None
        self.i = 0

    def previous_index(self):
        return self.division[self.i - 1]

    def next_index(self):
        return self.division[self.i + 1]

    def get_index(self):
        return self.division[self.i]

    def index_out_of_scope(self):
        print(f"out of scope check {self.i} {self.i < 0 or self.i >= (len(self.division))}\n")
        return self.i < 0 or self.i >= (len(self.division))

    def reset_index(self):
        self.i = 0


keep_data = DataKeeper()

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


def repeat_buttons(event_id):
    repeat_markup = InlineKeyboardMarkup(row_width=1)
    repeat_button = InlineKeyboardButton("Повторить", callback_data=f"repeat:{event_id}")
    repeat_markup.add(repeat_button)
    repeat_markup.add(close_btn)
    return repeat_markup


def change_buttons(item, item_id):
    change_markup = InlineKeyboardMarkup(row_width=1)
    attend_button = InlineKeyboardButton("Посещение", callback_data=f"show_attendance:{item_id}")
    change_button = InlineKeyboardButton("Изменить", callback_data=f"change:{item}:{item_id}")
    change_markup.add(attend_button)
    change_markup.add(change_button)
    change_markup.add(close_btn)
    return change_markup


def query_button(text, call_data):
    query_markup = InlineKeyboardMarkup()
    query_btn = InlineKeyboardButton(text, callback_data=call_data)
    query_markup.add(query_btn)
    return query_markup


def callback_buttons(data: List, row=2, multiple=False):
    """
    Create group of the buttons.
    data: [(text, callback_data)]
    row: int
    division: ((tuple<int>), int)
    """
    markup = InlineKeyboardMarkup(row_width=row)
    data_amount = len(data)

    if data_amount > ((keep_data.row_height + 1) * row):
        multiple = setup_multiple(data, data_amount, row)

    if multiple:
        buttons = [
            InlineKeyboardButton(text, callback_data=call)
            for text, call in data[keep_data.get_index():
                                   keep_data.get_index() + keep_data.row_height * row]
        ]

        next_btn, previous_btn = rolling_buttons("call", "None")
        markup.add(*buttons)
        markup.add(previous_btn, next_btn)

    else:
        buttons = [
            InlineKeyboardButton(text, callback_data=call)
            for text, call in data
        ]
        markup.add(*buttons)

    markup.add(close_btn)
    return markup


def message_buttons(data: List, event_id, row=2, multiple=None):
    """Creates markup with url buttons"""
    markup = InlineKeyboardMarkup(row_width=row)
    data_amount = len(data)

    if data_amount > ((keep_data.row_height + 1) * row):
        multiple = setup_multiple(data, data_amount, row)

    if multiple:
        buttons = [
            InlineKeyboardButton(f"{attendance} {fullname}", url=f"t.me/{telegram_name}")
            for fullname, telegram_name, attendance in data[keep_data.get_index():
                                                            keep_data.get_index() + keep_data.row_height * row]
        ]

        next_btn, previous_btn = rolling_buttons("url", event_id)
        markup.add(*buttons)
        markup.add(previous_btn, next_btn)

    else:
        buttons = [
            InlineKeyboardButton(f"{attendance} {fullname}", url=f"t.me/{telegram_name}")
            for fullname, telegram_name, attendance in data
        ]
        markup.add(*buttons)

    remove_btn = InlineKeyboardButton("Убрать участника", callback_data=f"remove_attendance:{event_id}")
    markup.add(remove_btn)
    markup.add(close_btn)
    return markup


def setup_multiple(data, data_amount, row):
    keep_data.data = data
    keep_data.division = [i for i in range(0, data_amount, keep_data.row_height * row)]
    keep_data.row = row
    print(f"inside setup_multiple row is {row}")
    if keep_data.index_out_of_scope():
        keep_data.reset_index()
    return True


def rolling_buttons(btn_type, event_id):
    previous_btn = InlineKeyboardButton(" ", callback_data=EMTPY_FIELD)
    next_btn = InlineKeyboardButton(" ", callback_data=EMTPY_FIELD)
    call_config = "buttons_roll"

    if keep_data.get_index():
        previous_btn = InlineKeyboardButton(
            prev_button_text,
            callback_data=f"{call_config}:previous:{btn_type}:{keep_data.previous_index()}:{event_id}"
        )

    if keep_data.get_index() < keep_data.division[-1]:
        next_btn = InlineKeyboardButton(
            next_button_text,
            callback_data=f"{call_config}:next:{btn_type}:{keep_data.next_index()}:{event_id}"
        )
    return next_btn, previous_btn


def singer_info_buttons(telegram_name, singer_id, btn_names):
    print(f"{telegram_name}, {singer_id}, {btn_names}")
    markup = InlineKeyboardMarkup(row_width=2)
    send_msg_btn = InlineKeyboardButton("Написать", url=f"t.me/{telegram_name}")
    buttons = [send_msg_btn]
    for i, text in enumerate(btn_names):
        btn = InlineKeyboardButton(text, callback_data=f"info:{i}:{singer_id}")
        buttons.append(btn)
    markup.add(*buttons)
    markup.add(close_btn)
    return markup
