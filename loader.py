import logging

from config import BOT_TOKEN
from telebot import TeleBot
from keyboards.inline import callback_datas
from handlers.users import filters

logging.basicConfig(level=logging.INFO)

bot = TeleBot(BOT_TOKEN)

bot.add_custom_filter(callback_datas.UserRegFilter())
bot.add_custom_filter(callback_datas.UserSearchFilter())
bot.add_custom_filter(filters.NewUserFilter())

