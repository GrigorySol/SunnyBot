from telebot.callback_data import CallbackData
from misc.dictionaries import callback_dictionary as cd

# calendar
calendar_data = CallbackData("event_type", "event_id", "year", "month", "day", prefix=cd.calendar_data_text)
calendar_factory = CallbackData("event_type", "event_id", "year", "month", prefix=cd.calendar_factory_text)
calendar_zoom = CallbackData("event_type", "event_id", "year", prefix=cd.calendar_zoom_text)

# event
show_event_callback = CallbackData("event_id", prefix=cd.event_display_text)
repeat_callback = CallbackData("event_id", prefix=cd.event_repeat_text)
interval_callback = CallbackData("event_id", "repeat_id", prefix=cd.event_interval_text)
upcoming_month = CallbackData("year", "month", "day", prefix=cd.upcoming_month_text)
spam_month = CallbackData("year", "month", "day", prefix=cd.spam_month_text)

# changes
add_new_callback = CallbackData("type", prefix=cd.add_new_text)
change_callback = CallbackData("type", "item_id", prefix=cd.change_item_text)
selected_callback = CallbackData("option_id", "event_id", prefix=cd.selected_text)
selected_location_callback = CallbackData("option_id", "location_id", prefix=cd.selected_location_text)
selected_suit_callback = CallbackData("option_id", "suit_id", prefix=cd.selected_suit_text)

change_songs_callback = CallbackData("concert_id", "option_id", prefix=cd.change_songs_text)
concert_songs_callback = CallbackData("option", "concert_id", "song_id", prefix=cd.concert_songs_text)
remove_suit_callback = CallbackData("concert_id", "option_id", prefix=cd.remove_suit_text)
select_suit_callback = CallbackData("concert_id", "option_id", prefix=cd.select_suit_text)

# songs
song_filter_callback = CallbackData("filter_id", prefix=cd.song_filter_text)
concert_filter_callback = CallbackData("filter_id", prefix=cd.concert_filter_text)
song_info_callback = CallbackData("song_id", prefix=cd.song_info_text)
edit_song_callback = CallbackData("song_id", "option_id", prefix=cd.edit_song_text)
edit_song_material_callback = CallbackData("song_id", "option_id", "edit_id", prefix=cd.edit_song_material_text)

# locations
add_event_location_callback = CallbackData("type", "event_id", prefix=cd.add_event_location_text)
edit_location_callback = CallbackData("location_id", prefix=cd.edit_location_text)

# singer
register_callback = CallbackData(prefix=cd.singer_registration_text)
search_callback = CallbackData("type", prefix=cd.singer_search_text)
show_singer_callback = CallbackData("singer_id", prefix=cd.singer_display_text)
voice_callback = CallbackData("voice_id", prefix=cd.singer_voice_text)
edit_voice_callback = CallbackData("action", "voice_id", prefix=cd.singer_edit_voice_text)
display_suit_photos_callback = CallbackData(prefix=cd.display_suit_photos_text)
display_suit_buttons_callback = CallbackData(prefix=cd.display_suit_buttons_text)
singer_suit_callback = CallbackData("action", "singer_id", prefix=cd.singer_suit_text)
info_callback = CallbackData("name", "singer_id", prefix=cd.singer_info_text)
singer_add_callback = CallbackData("item_type", "singer_id", "item_id", prefix=cd.singer_add_action_text)
singer_remove_callback = CallbackData("item_type", "singer_id", "item_id", prefix=cd.singer_remove_action_text)
unblock_user_callback = CallbackData("singer_id", prefix=cd.unblock_user_text)
edit_admin_callback = CallbackData("option", prefix=cd.admin_edit_text)
add_remove_admin_callback = CallbackData("option", "singer_id", prefix=cd.add_remove_admin_text)

# attendance
attendance_intervals_callback = CallbackData("interval", "singer_id", prefix=cd.attendance_intervals_text)
show_participation_callback = CallbackData("event_id", prefix=cd.show_participation_text)
add_participant_callback = CallbackData("event_id", prefix=cd.add_participant_text)
add_all_participants_callback = CallbackData("event_id", prefix=cd.add_all_participants_text)
remove_participation_callback = CallbackData("event_id", prefix=cd.remove_participation_text)
remove_all_participants_callback = CallbackData("event_id", prefix=cd.remove_all_participants_text)
singer_attendance_callback = CallbackData("action", "event_id", "option", prefix=cd.singer_attendance_text)
mass_edit_attendance_callback = CallbackData("event_id", "decision", prefix=cd.mass_edit_attendance_text)

delete_confirmation_callback = CallbackData("item_type", "item_id", "action_id", prefix=cd.delete_confirmation_text)

buttons_roll_callback = CallbackData("roll_bar_id", "direction", "index", "event_id", prefix=cd.buttons_roll_text)
close_button = CallbackData("roll_bar_id", prefix=cd.close_text)
