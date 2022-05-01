import logging

from config import BOT_TOKEN
from telebot import TeleBot
from handlers.singers import filters

logging.basicConfig(level=logging.INFO)

bot = TeleBot(BOT_TOKEN)

bot.add_custom_filter(filters.SingerConfigFilter())
bot.add_custom_filter(filters.NewSingerFilter())

