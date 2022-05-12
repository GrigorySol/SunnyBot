from telebot.callback_data import CallbackData


calendar_data = CallbackData("event_id", "year", "month", "day", "_id", prefix="calendar_data")
calendar_factory = CallbackData("event_id", "year", "month", prefix="calendar_factory")
calendar_zoom = CallbackData("event_id", "year", prefix="calendar_zoom")


event_callback = CallbackData("eid", prefix="event")
repeat_callback = CallbackData("eid", prefix="repeat")
period_callback = CallbackData("eid", "repeat_id", prefix="period")

add_new_callback = CallbackData("type", prefix="add_new")
change_callback = CallbackData("type", "id", prefix="change")
selected_event_callback = CallbackData("option_id", "event_id", prefix="selected_event")
selected_location_callback = CallbackData("option_id", "location_id", prefix="selected_location")

change_songs_callback = CallbackData("concert_id", "option_id", prefix="change_songs")
concert_songs_callback = CallbackData("option", "concert_id", "song_id", prefix="concert_songs")

song_filter_callback = CallbackData("filter_id", prefix="song_filter")
concert_filter_callback = CallbackData("filter_id", prefix="concert_filter")
song_info_callback = CallbackData("song_id", prefix="song_info")
edit_song_callback = CallbackData("song_id", "option_id", prefix="edit_song")
edit_song_material_callback = CallbackData("song_id", "option_id", "edit_id", prefix="edit_song_material")

location_callback = CallbackData("type", prefix="location")
edit_location_callback = CallbackData("location_id", prefix="edit_location")

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")
show_singer_callback = CallbackData("s_id", prefix="show_singer")
voice_callback = CallbackData("voice_id", prefix="voice")
edit_voice_callback = CallbackData("action", "voice_id", prefix="voice")
suit_edit_callback = CallbackData("action", "suit_id", prefix="suit")
info_callback = CallbackData("name", "singer_id", prefix="info")
singer_add_callback = CallbackData("type", "singer_id", "item_id", prefix="singer_add")
singer_remove_callback = CallbackData("type", "singer_id", "item_id", prefix="singer_remove")

delete_confirmation_callback = CallbackData("type", "item_id", "action_id", prefix="delete_confirmation")
