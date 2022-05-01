from telebot.callback_data import CallbackData

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
info_callback = CallbackData("type", prefix="info")
