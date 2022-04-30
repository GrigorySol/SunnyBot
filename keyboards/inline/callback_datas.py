from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot import types, AdvancedCustomFilter

register_callback = CallbackData(prefix="registration")
search_callback = CallbackData("type", prefix="search")


class UserRegFilter(AdvancedCustomFilter):
    key = 'user_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class UserSearchFilter(AdvancedCustomFilter):
    key = 'user_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
