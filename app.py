from threading import Thread

if __name__ == "__main__":
    from handlers import bot
    from misc import reminder
    # Thread(target=reminder.schedule_pending).start()
    # bot.infinity_polling()
