from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Regular buttons
confirm_btn = InlineKeyboardButton("Да", callback_data="confirm")
decline_btn = InlineKeyboardButton("Нет", callback_data="decline")
cancel_btn = InlineKeyboardButton("Отмена", callback_data="cancel")
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
search_by_name = InlineKeyboardButton("По имени", callback_data="search:singer_name")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")  # Alternate input for callback
search_choice.add(search_by_name, search_by_voice, show_all_btn)

# Voice choice buttons
voices_dict = {"1 soprano": "1 сопрано",
               "2 soprano": "2 сопрано",
               "mezzo": "меццо",
               "alto": "альт",
               "tenor": "тенор",
               "bass": "бас"}
voice_choice = InlineKeyboardMarkup(row_width=2)
voice_choice.add(*[InlineKeyboardButton(voices_dict[voice], callback_data=voice) for voice in voices_dict])


def naming_buttons(singers):
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for singer in singers:
        btn = InlineKeyboardButton(f"{singer[1]} {singer[2]}", url=f"t.me/{singer[0]}")
        buttons.append(btn)
    markup.add(*buttons)
    return markup

