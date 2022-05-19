import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP = os.getenv("THE_ONE")
PASS_PHRASE = os.getenv("SECURITY_ANSWER")
SECRET_PASS_PHRASE = os.getenv("ADMIN_ANSWER")
