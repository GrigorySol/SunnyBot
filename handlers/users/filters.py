from telebot.custom_filters import SimpleCustomFilter
from telebot.types import Message
from db import BotDB

BotDB = BotDB('sunny_bot.db')


class NewUserFilter(SimpleCustomFilter):
    """Check whether the user is new"""

    key = "is_new_user"

    def check(self, message: Message):
        user_id = message.from_user.id
        exists = BotDB.user_exists(user_id)
        return not exists
