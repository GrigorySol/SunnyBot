import os
from dotenv import load_dotenv

from database_control import db_creation


if not os.path.exists("database_control/sunny_bot.db"):
    db_creation.create_database()

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP = os.getenv("THE_ONE")
VIP2 = os.getenv("THE_SECOND")
PASS_PHRASE = os.getenv("SECURITY_ANSWER")
SECRET_PASS_PHRASE = os.getenv("ADMIN_ANSWER")
