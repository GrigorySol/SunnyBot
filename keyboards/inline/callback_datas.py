from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot import types, AdvancedCustomFilter

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")


class SingerRegFilter(AdvancedCustomFilter):
    key = 'singer_config'

    def check(self, call: types.CallbackQuery, singer: CallbackDataFilter):
        return singer.check(query=call)


class SingerSearchFilter(AdvancedCustomFilter):
    key = 'singer_config'

    def check(self, call: types.CallbackQuery, singer: CallbackDataFilter):
        return singer.check(query=call)
