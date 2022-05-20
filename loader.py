import logging
import sys

from config import BOT_TOKEN
from telebot import TeleBot
from handlers.singers import filters

logging.basicConfig(level=logging.ERROR)


sys.excepthook = logging.exception

bot = TeleBot(BOT_TOKEN)

bot.add_custom_filter(filters.SingerConfigFilter())
bot.add_custom_filter(filters.NewSingerFilter())
bot.add_custom_filter(filters.UserBlocked())
bot.add_custom_filter(filters.CalendarCallbackFilter())
