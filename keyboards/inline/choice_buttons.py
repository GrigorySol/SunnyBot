from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from misc.messages.event_dictionary import next_button_text, prev_button_text
from misc.messages import buttons_dictionary as bu_d

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

close_btn = InlineKeyboardButton(bu_d.close_btn_text, callback_data="close")

close_markup = InlineKeyboardMarkup()
close_markup.add(close_btn)

# New singer buttons
new_singer_markup = InlineKeyboardMarkup(row_width=2)
add_singer = InlineKeyboardButton(bu_d.register_btn_text, callback_data="registration")
new_singer_markup.add(add_singer)
new_singer_markup.add(close_btn)

# Singer search choice buttons
search_choice_markup = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton(bu_d.singer_filter_btn_text_tuple[0], switch_inline_query_current_chat="а")
search_by_voice = InlineKeyboardButton(bu_d.singer_filter_btn_text_tuple[1], callback_data="search:voice")
show_all_btn = InlineKeyboardButton(bu_d.singer_filter_btn_text_tuple[2], callback_data="show_all")
search_choice_markup.add(search_by_name, search_by_voice, show_all_btn)
search_choice_markup.add(close_btn)

# Reply with joke
accept_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes_btn = KeyboardButton(bu_d.accept_btn_text_tuple[0])
of_course_btn = KeyboardButton(bu_d.accept_btn_text_tuple[1])
accept_markup.add(yes_btn, of_course_btn, close_btn)

# choose old or new location buttons
choose_location_markup = InlineKeyboardMarkup(row_width=2)
choose_old = InlineKeyboardButton(bu_d.choose_location_btn_text_tuple[0], callback_data="add_event_location:db")
get_url = InlineKeyboardButton(bu_d.choose_location_btn_text_tuple[1], callback_data="add_event_location:url")
choose_location_markup.add(choose_old, get_url)
choose_location_markup.add(close_btn)


def show_participation(event_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    singers_button = InlineKeyboardButton(
        bu_d.show_participation_btn_text, callback_data=f"show_participation:{event_id}"
    )
    markup.add(singers_button)
    return markup


def add_concert_songs_buttons(concert_id):
    concert_markup = InlineKeyboardMarkup(row_width=1)
    add_songs_button = InlineKeyboardButton(
        bu_d.add_songs_btn_text, callback_data=f"change_songs:{concert_id}:0"
    )
    concert_markup.add(add_songs_button)
    concert_markup.add(close_btn)
    return concert_markup


def repeat_buttons(event_id):
    repeat_markup = InlineKeyboardMarkup(row_width=1)
    repeat_button = InlineKeyboardButton(
        bu_d.repeat_btn_text, callback_data=f"repeat:{event_id}"
    )
    repeat_markup.add(repeat_button)
    repeat_markup.add(close_btn)
    return repeat_markup


def change_buttons(item_type, item_id):
    change_markup = InlineKeyboardMarkup(row_width=1)
    change_button = InlineKeyboardButton(
        bu_d.event_change_btn_text, callback_data=f"change:{item_type}:{item_id}"
    )
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


def participant_message_buttons(data: List, event_id, row=2, multiple=None):
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

    add_one_btn = InlineKeyboardButton(bu_d.event_add_singer_btn_text,
                                       callback_data=f"add_participant:{event_id}")
    remove_one_btn = InlineKeyboardButton(bu_d.event_remove_singer_btn_text,
                                          callback_data=f"remove_participation:{event_id}")
    add_all_btn = InlineKeyboardButton(bu_d.event_add_all_btn_text,
                                       callback_data=f"add_all_participants:{event_id}")
    remove_all_btn = InlineKeyboardButton(bu_d.event_remove_all_btn_text,
                                          callback_data=f"remove_all_participants:{event_id}")

    markup.add(add_one_btn, remove_one_btn)
    markup.add(add_all_btn)
    markup.add(remove_all_btn)
    markup.add(close_btn)
    return markup


def empty_participant_buttons(event_id, row=2):
    """Creates markup with url buttons"""
    markup = InlineKeyboardMarkup(row_width=row)

    add_one_btn = InlineKeyboardButton(bu_d.event_add_singer_btn_text,
                                       callback_data=f"add_participant:{event_id}")
    add_all_btn = InlineKeyboardButton(bu_d.event_add_all_btn_text,
                                       callback_data=f"add_all_participants:{event_id}")

    markup.add(add_one_btn)
    markup.add(add_all_btn)
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
    send_msg_btn = InlineKeyboardButton(bu_d.send_msg_btn_text, url=f"t.me/{telegram_name}")
    buttons = [send_msg_btn]
    for i, text in enumerate(btn_names):
        btn = InlineKeyboardButton(text, callback_data=f"info:{i}:{singer_id}")
        buttons.append(btn)
    markup.add(*buttons)
    markup.add(close_btn)
    return markup
