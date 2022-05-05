from telebot.callback_data import CallbackData

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
singer_callback = CallbackData("s_id", prefix="singer")
voice_callback = CallbackData("voice_id", prefix="voice")
suit_callback = CallbackData("action", "suit_id", prefix="suit")
info_callback = CallbackData("name", "singer_id", prefix="info")
add_callback = CallbackData("type", "singer_id", "item_id", prefix="add")
remove_callback = CallbackData("type", "singer_id", "item_id", prefix="remove")
