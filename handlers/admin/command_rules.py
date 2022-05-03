from loader import bot
from telebot.types import BotCommand, BotCommandScopeChat
from misc.bot_commands import admin_commands, singer_commands
from db import BotDB

BotDB = BotDB("sunny_bot.db")

s_commands = []
for s_command in singer_commands:
    bot_s_command = BotCommand(s_command, singer_commands[s_command])
    s_commands.append(bot_s_command)

bot.set_my_commands(s_commands)


def admin_command_rules():
    commands = []
    for command in admin_commands:
        bot_command = BotCommand(command, admin_commands[command])
        commands.append(bot_command)

    admins = BotDB.get_all_admins()
    admin_chats = []
    for admin in admins:
        print(admin)
        chat = BotCommandScopeChat(admin)
        admin_chats.append(chat)

    for admin_chat in admin_chats:
        bot.set_my_commands(
            commands=commands,
            scope=admin_chat
        )


admin_command_rules()
