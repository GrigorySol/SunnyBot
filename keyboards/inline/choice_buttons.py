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

# New user buttons
new_user_markup = InlineKeyboardMarkup(row_width=2)
add_user = InlineKeyboardButton("Зарегистрироваться", callback_data="registration")
new_user_markup.add(add_user)
new_user_markup.add(cancel_btn)

# User search choice buttons
search_choice = InlineKeyboardMarkup(row_width=2)
search_by_name = InlineKeyboardButton("По имени", callback_data="search:user_name")
search_by_voice = InlineKeyboardButton("По голосу", callback_data="search:voice")  # Alternate input for callback
search_choice.add(search_by_name)
search_choice.add(search_by_voice)
search_choice.add(show_all_btn)

# Voice choice buttons
voices_dict = {"1 soprano": "1 сопрано",
               "2 soprano": "2 сопрано",
               "mezzo": "меццо",
               "alto": "альт",
               "tenor": "тенор",
               "bass": "бас"}
voice_choice = InlineKeyboardMarkup(row_width=2)
for voice in voices_dict:
    btn = InlineKeyboardButton(voices_dict[voice], callback_data=voice)
    voice_choice.add(btn)

