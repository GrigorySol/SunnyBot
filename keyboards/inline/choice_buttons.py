from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union, List, Tuple

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

# singer search choice buttons
search_choice = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton("По имени", switch_inline_query_current_chat="бас")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")
show_all_btn = InlineKeyboardButton("Посмотреть всех", callback_data="show_all")
search_choice.add(search_by_name, search_by_voice, show_all_btn)
search_choice.add(close_btn)


def callback_buttons(data: Union[List, Tuple], call_data=None, row=2):
    """Create group of the buttons"""
    markup = InlineKeyboardMarkup(row_width=row)
    buttons = []
    for text in data:
        if not call_data:
            call_data = text
            btn = InlineKeyboardButton(text, callback_data=call_data)        # url=f"t.me/{singer[0]}"
            buttons.append(btn)
            call_data = None
        else:
            btn = InlineKeyboardButton(text, callback_data=call_data)        # url=f"t.me/{singer[0]}"
            buttons.append(btn)
    markup.add(*buttons)
    return markup


def singer_info_buttons(singername):
    markup = InlineKeyboardMarkup(row_width=2)
    send_msg_btn = InlineKeyboardButton("Написать", url=f"t.me/{singername}")
    voice_btn = InlineKeyboardButton("Голос", callback_data="info:voice")
    suit_btn = InlineKeyboardButton("Костюмы", callback_data="info:suit")
    attend_btn = InlineKeyboardButton("Посещаемость", callback_data="info:attend")
    comment_btn = InlineKeyboardButton("Комментарий", callback_data="info:comment")
    delete_btn = InlineKeyboardButton("УДАЛИТЬ", callback_data="info:delete")
    markup.add(send_msg_btn, voice_btn, suit_btn, attend_btn, comment_btn, delete_btn)
    markup.add(close_btn)
    return markup

