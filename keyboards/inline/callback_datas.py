from telebot.callback_data import CallbackData

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
singer_callback = CallbackData("s_id", prefix="singer")
voice_callback = CallbackData("v_id", prefix="voice")
info_callback = CallbackData("name", "singerid", prefix="info")
