import os
from dotenv import load_dotenv

if not os.path.exists(".env"):
    raise ImportError("File '.env' not found. Add '.env' to the bot directory.")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_DB = os.getenv("BOT_DB")
VIP = os.getenv("THE_ONE")
VIP2 = os.getenv("THE_SECOND")
PASS_PHRASE = os.getenv("SECURITY_ANSWER")
SECRET_PASS_PHRASE = os.getenv("ADMIN_ANSWER")
MENU_IMAGE = os.getenv("MENU_IMAGE")

if not os.path.exists(BOT_DB):
    from database_control import db_creation
    db_creation.create_database()
