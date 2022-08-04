from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from misc.messages.event_dictionary import next_button_text, prev_button_text
from misc.messages import buttons_dictionary as but_d
from misc import callback_dict as cd

EMTPY_FIELD = 'calendar_button'


class ButtonsKeeper:
    _btn_msgs = {}

    def __new__(cls, message_id):
        if (data := cls._btn_msgs.get(message_id)) is not None:
            return data
        data = super().__new__(cls)
        cls._btn_msgs[message_id] = data
        data._save_data()
        return data

    def _save_data(self):
        self.data = None
        self.row = None
        self.division = None
        self.i = 0

    def previous_index(self):
        return self.division[self.i - 1]

    def next_index(self):
        return self.division[self.i + 1]

    def get_index(self):
        return self.division[self.i]

    @classmethod
    def data_exists(cls, message_id):
        return message_id in cls._btn_msgs

    @classmethod
    def delete_btn(cls, message_id):
        cls._btn_msgs.pop(message_id, None)


# def callback_buttons(*args):
#     pass


# keep_data = DataKeeper()

# Regular buttons

close_btn = InlineKeyboardButton(but_d.close_btn_text, callback_data=cd.close_text)

close_markup = InlineKeyboardMarkup()
close_markup.add(close_btn)

# New singer buttons
new_singer_markup = InlineKeyboardMarkup(row_width=2)
add_singer = InlineKeyboardButton(but_d.register_btn_text, callback_data=cd.singer_registration_text)
new_singer_markup.add(add_singer)
new_singer_markup.add(close_btn)

# Singer search choice buttons
search_choice_markup = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton(but_d.singer_filter_btn_text_tuple[0], switch_inline_query_current_chat="а")
search_by_voice = InlineKeyboardButton(but_d.singer_filter_btn_text_tuple[1],
                                       callback_data=f"{cd.singer_search_text}:voice")
show_all_btn = InlineKeyboardButton(but_d.singer_filter_btn_text_tuple[2], callback_data=cd.singer_show_all_text)
search_choice_markup.add(search_by_name, search_by_voice, show_all_btn)
search_choice_markup.add(close_btn)

# Reply with joke
accept_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
yes_btn = KeyboardButton(but_d.accept_btn_text_tuple[0])
of_course_btn = KeyboardButton(but_d.accept_btn_text_tuple[1])
accept_markup.add(yes_btn, of_course_btn, close_btn)


def buttons_markup(
        data, message_id, event_id=None, menu_btn=False, participant=False, multiple=False, row=2, line=5
):
    markup = InlineKeyboardMarkup(row_width=row)
    data_amount = len(data)

    if data_amount > line * row:
        multiple = set_multiple(data, message_id, data_amount, row, line)

    if multiple:
        keep_buttons_data = ButtonsKeeper(message_id)
        buttons = [
            InlineKeyboardButton(**kwargs)
            for kwargs in data[keep_buttons_data.get_index():
                               keep_buttons_data.get_index() + row * line]
        ]

        next_btn, previous_btn = rolling_buttons("None", message_id)
        markup.add(*buttons)
        markup.add(previous_btn, next_btn)

    else:
        buttons = [
            InlineKeyboardButton(**kwargs)
            for kwargs in data
        ]
        markup.add(*buttons)

    if participant:
        add_remove_participant(markup, event_id=event_id)

    if menu_btn:
        call_btn = f"{cd.change_item_text}:event:{event_id}"
        go_btn = InlineKeyboardButton(but_d.go_menu_btn_text, callback_data=call_btn)
        markup.add(go_btn)

    markup.add(close_btn)
    return markup


def add_remove_participant(markup, event_id):
    add_one_btn = InlineKeyboardButton(but_d.event_add_singer_btn_text,
                                       callback_data=f"{cd.add_participant_text}:{event_id}")
    remove_one_btn = InlineKeyboardButton(but_d.event_remove_singer_btn_text,
                                          callback_data=f"{cd.remove_participation_text}:{event_id}")
    add_all_btn = InlineKeyboardButton(but_d.event_add_all_btn_text,
                                       callback_data=f"{cd.add_all_participants_text}:{event_id}")
    remove_all_btn = InlineKeyboardButton(but_d.event_remove_all_btn_text,
                                          callback_data=f"{cd.remove_all_participants_text}:{event_id}")

    markup.add(add_one_btn, remove_one_btn)
    markup.add(add_all_btn, remove_all_btn)


def set_multiple(data, message_id, data_amount, row, line):
    keep_buttons_data = ButtonsKeeper(message_id)
    keep_buttons_data.data = data
    keep_buttons_data.row = row
    keep_buttons_data.division = [i for i in range(0, data_amount, row * line)]
    return True


def choose_location(event_id):
    markup = InlineKeyboardMarkup(row_width=2)
    choose_old = InlineKeyboardButton(
        but_d.choose_location_btn_text_tuple[0], callback_data=f"{cd.add_event_location_text}:db:{event_id}"
    )
    get_url = InlineKeyboardButton(
        but_d.choose_location_btn_text_tuple[1], callback_data=f"{cd.add_event_location_text}:url:{event_id}"
    )
    markup.add(choose_old, get_url)
    markup.add(go_menu_button(event_id, "event"))
    markup.add(close_btn)
    return markup


def show_participation(event_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    singers_button = InlineKeyboardButton(
        but_d.show_participation_btn_text, callback_data=f"{cd.show_participation_text}:{event_id}"
    )
    markup.add(singers_button)
    return markup


def add_songs_to_concert_buttons(concert_id):
    concert_markup = InlineKeyboardMarkup(row_width=1)
    add_songs_button = InlineKeyboardButton(
        but_d.add_songs_btn_text, callback_data=f"{cd.change_songs_text}:{concert_id}:0"
    )
    concert_markup.add(add_songs_button)
    concert_markup.add(go_menu_button(concert_id, "event"))
    concert_markup.add(close_btn)
    return concert_markup


def repeat_buttons(event_id):
    repeat_markup = InlineKeyboardMarkup(row_width=1)
    repeat_button = InlineKeyboardButton(
        but_d.repeat_btn_text, callback_data=f"{cd.event_repeat_text}:{event_id}"
    )
    repeat_markup.add(repeat_button)
    repeat_markup.add(close_btn)
    return repeat_markup


def change_buttons(item_type, item_id):
    change_markup = InlineKeyboardMarkup(row_width=1)
    change_button = InlineKeyboardButton(
        but_d.event_change_btn_text, callback_data=f"{cd.change_item_text}:{item_type}:{item_id}"
    )
    change_markup.add(change_button)
    change_markup.add(close_btn)
    return change_markup


def query_button(text, call_data):
    query_markup = InlineKeyboardMarkup()
    query_btn = InlineKeyboardButton(text, callback_data=call_data)
    query_markup.add(query_btn)
    return query_markup


def empty_participant_buttons(event_id, row=2):
    """Create markup add one and add all buttons"""

    markup = InlineKeyboardMarkup(row_width=row)

    add_one_btn = InlineKeyboardButton(but_d.event_add_singer_btn_text,
                                       callback_data=f"{cd.add_participant_text}:{event_id}")
    add_all_btn = InlineKeyboardButton(but_d.event_add_all_btn_text,
                                       callback_data=f"{cd.add_all_participants_text}:{event_id}")

    markup.add(add_one_btn)
    markup.add(add_all_btn)
    markup.add(go_menu_button(event_id, "event"))
    markup.add(close_btn)
    return markup


def add_remove_participant_buttons(event_id, add=True):
    """Create add or remove button"""

    if add:
        button = InlineKeyboardButton(
            but_d.event_add_singer_btn_text, callback_data=f"{cd.add_participant_text}:{event_id}"
        )
    else:
        button = InlineKeyboardButton(
            but_d.event_remove_singer_btn_text, callback_data=f"{cd.remove_participation_text}:{event_id}"
        )

    return button


def go_menu_button(item_id, item_type):
    """Create type change menu button"""

    return InlineKeyboardButton(but_d.go_menu_btn_text, callback_data=f"{cd.change_item_text}:{item_type}:{item_id}")


# def setup_multiple(data, data_amount, row):
#     keep_data.data = data
#     keep_data.division = [i for i in range(0, data_amount, ROW_HEIGHT * row)]
#     keep_data.row = row
#     print(f"inside setup_multiple row is {row}")
#     if keep_data.index_out_of_scope():
#         keep_data.reset_index()
#     return True


def rolling_buttons(event_id, message_id=0):
    previous_btn = InlineKeyboardButton(" ", callback_data=EMTPY_FIELD)
    next_btn = InlineKeyboardButton(" ", callback_data=EMTPY_FIELD)
    call_config = cd.buttons_roll_text

    keep_buttons_data = ButtonsKeeper(message_id)

    if keep_buttons_data.get_index():
        previous_btn = InlineKeyboardButton(
            prev_button_text,
            callback_data=f"{call_config}:previous:{keep_buttons_data.previous_index()}:{event_id}"
        )

    if keep_buttons_data.get_index() < keep_buttons_data.division[-1]:
        next_btn = InlineKeyboardButton(
            next_button_text,
            callback_data=f"{call_config}:next:{keep_buttons_data.next_index()}:{event_id}"
        )
    return next_btn, previous_btn


# def singer_info_buttons(telegram_name, singer_id, btn_names):
#     print(f"{telegram_name}, {singer_id}, {btn_names}")
#     markup = InlineKeyboardMarkup(row_width=2)
#     send_msg_btn = InlineKeyboardButton(but_d.send_msg_btn_text, url=f"t.me/{telegram_name}")
#     buttons = [send_msg_btn]
#     for i, text in enumerate(btn_names):
#         btn = InlineKeyboardButton(text, callback_data=f"{cd.singer_info_text}:{i}:{singer_id}")
#         buttons.append(btn)
#     markup.add(*buttons)
#     markup.add(close_btn)
#     return markup
