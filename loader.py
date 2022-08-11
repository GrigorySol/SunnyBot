import logging
import os

from config import BOT_TOKEN
from telebot import TeleBot, custom_filters
from handlers.singers import filters

log = logging
log.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

bot = TeleBot(BOT_TOKEN)

JOKES = []
if os.path.exists("jokes.txt"):
    file = open("jokes.txt")
    jokes = file.readlines()
    file.close()
    JOKES = [joke for joke in jokes]

bot.add_custom_filter(filters.SingerConfigFilter())
bot.add_custom_filter(filters.NewSingerFilter())
bot.add_custom_filter(filters.UserBlocked())
bot.add_custom_filter(filters.CalendarCallbackFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())
