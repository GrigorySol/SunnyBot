from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message
from db import BotDB

BotDB = BotDB('sunny_bot.db')


class NewsingerFilter(SimpleCustomFilter):
    """Check whether the singer is new"""

    key = "is_new_singer"

    def check(self, message: Message):
        singer_id = message.from_user.id
        exists = BotDB.singer_exists(singer_id)
        return not exists
