from telebot.callback_data import CallbackData


calendar_data = CallbackData("event_id", "year", "month", "day", prefix="calendar_data")
calendar_factory = CallbackData("event_id", "year", "month", prefix="calendar_factory")
calendar_zoom = CallbackData("event_id", "year", prefix="calendar_zoom")

event_callback = CallbackData("eid", prefix="event")
repeat_callback = CallbackData("eid", prefix="repeat")

location_callback = CallbackData("type", prefix="location")

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
singer_callback = CallbackData("s_id", prefix="singer")
voice_callback = CallbackData("voice_id", prefix="voice")
voice_edit_callback = CallbackData("action", "voice_id", prefix="voice")
suit_edit_callback = CallbackData("action", "suit_id", prefix="suit")
info_callback = CallbackData("name", "singer_id", prefix="info")
add_callback = CallbackData("type", "singer_id", "item_id", prefix="add")
remove_callback = CallbackData("type", "singer_id", "item_id", prefix="remove")
