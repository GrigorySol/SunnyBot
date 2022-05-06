from telebot.callback_data import CallbackDataFilter
from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter
from telebot.types import Message, CallbackQuery
from database_control.db_singer import singer_exists


class NewSingerFilter(SimpleCustomFilter):
    """Check whether the singer is new"""

    key = "is_new_singer"

    def check(self, message: Message):
        singer_id = message.from_user.id
        exists = singer_exists(singer_id)
        return not exists


class SingerConfigFilter(AdvancedCustomFilter):
    key = 'singer_config'

    def check(self, call: CallbackQuery, singer: CallbackDataFilter):
        return singer.check(query=call)


class CalendarCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class CalendarZoomCallbackFilter(AdvancedCustomFilter):
    key = 'calendar_zoom_config'

    def check(self, call: CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)



