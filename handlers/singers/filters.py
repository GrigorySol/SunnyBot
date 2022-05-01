from telebot.callback_data import CallbackDataFilter
from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter
from telebot.types import Message, CallbackQuery
from db import BotDB

BotDB = BotDB('sunny_bot.db')


class NewSingerFilter(SimpleCustomFilter):
    """Check whether the singer is new"""

    key = "is_new_singer"

    def check(self, message: Message):
        singer_id = message.from_user.id
        exists = BotDB.singer_exists(singer_id)
        return not exists


class SingerConfigFilter(AdvancedCustomFilter):
    key = 'singer_config'

    def check(self, call: CallbackQuery, singer: CallbackDataFilter):
        return singer.check(query=call)
