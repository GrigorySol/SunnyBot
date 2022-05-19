from telebot.callback_data import CallbackDataFilter
from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter
from telebot.types import Message, CallbackQuery
from database_control.db_singer import singer_exists, is_blocked


class UserBlocked(SimpleCustomFilter):
    """Check whether the user is blocked"""

    key = "is_blocked"

    def check(self, message: Message):
        blocked = is_blocked(message.from_user.id)
        return blocked


class NewSingerFilter(SimpleCustomFilter):
    """Check whether the singer is new"""

    key = "is_new_singer"

    def check(self, message: Message):
        exists = singer_exists(message.from_user.id)
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



