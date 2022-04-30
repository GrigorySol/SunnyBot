import logging

from config import BOT_TOKEN
from telebot import TeleBot
from keyboards.inline import callback_datas
from handlers.singers import filters

logging.basicConfig(level=logging.INFO)

bot = TeleBot(BOT_TOKEN)

bot.add_custom_filter(callback_datas.SingerRegFilter())
bot.add_custom_filter(callback_datas.SingerSearchFilter())
bot.add_custom_filter(filters.NewsingerFilter())

