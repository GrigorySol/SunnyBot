from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union, List, Tuple, Dict

# Regular buttons
confirm_btn = InlineKeyboardButton("Да", callback_data="confirm")
decline_btn = InlineKeyboardButton("Нет", callback_data="decline")
cancel_btn = InlineKeyboardButton("Закрыть", callback_data="close")
back_btn = InlineKeyboardButton("Вернуться в меню", callback_data="back")
show_all_btn = InlineKeyboardButton("Посмотреть всех", callback_data="show_all")

# Confirmation buttons
confirm_markup = InlineKeyboardMarkup(row_width=2)
confirm_markup.add(confirm_btn)
confirm_markup.add(decline_btn)

# New singer buttons
new_singer_markup = InlineKeyboardMarkup(row_width=2)
add_singer = InlineKeyboardButton("Зарегистрироваться", callback_data="registration")
new_singer_markup.add(add_singer)
new_singer_markup.add(cancel_btn)

# singer search choice buttons
search_choice = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton("По имени", switch_inline_query_current_chat="бас")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")  # Alternate input for callback
search_choice.add(search_by_name, search_by_voice, show_all_btn)
search_choice.add(cancel_btn)


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


def singer_info_buttons():
    markup = InlineKeyboardMarkup(row_width=2)
    return

