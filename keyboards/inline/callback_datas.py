from telebot.callback_data import CallbackData


calendar_data = CallbackData("event_id", "year", "month", "day", prefix="calendar_data")
calendar_factory = CallbackData("event_id", "year", "month", prefix="calendar_factory")
calendar_zoom = CallbackData("event_id", "year", prefix="calendar_zoom")


event_callback = CallbackData("eid", prefix="event")
repeat_callback = CallbackData("eid", prefix="repeat")
period_callback = CallbackData("eid", prefix="period")

add_new_callback = CallbackData("type", prefix="add_new")

location_callback = CallbackData("type", prefix="location")

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
show_singer_callback = CallbackData("s_id", prefix="show_singer")
voice_callback = CallbackData("voice_id", prefix="voice")
edit_voice_callback = CallbackData("action", "voice_id", prefix="voice")
suit_edit_callback = CallbackData("action", "suit_id", prefix="suit")
info_callback = CallbackData("name", "singer_id", prefix="info")
singer_add_callback = CallbackData("type", "singer_id", "item_id", prefix="singer_add")
singer_remove_callback = CallbackData("type", "singer_id", "item_id", prefix="singer_remove")
