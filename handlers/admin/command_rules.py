from loader import bot
from telebot.types import BotCommand, BotCommandScopeChat
from misc.bot_commands import admin_commands, singer_commands
from database_control.db_singer import get_all_admins


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

    for s_command in s_commands:
        commands.append(s_command)

    admins = get_all_admins()
    admin_chats = []
    for admin in admins:
        print(admin[0])
        bot.delete_my_commands(BotCommandScopeChat(admin[0]))
        chat = BotCommandScopeChat(admin[0])
        admin_chats.append(chat)

    for admin_chat in admin_chats:
        bot.set_my_commands(
            commands=commands,
            scope=admin_chat
        )


admin_command_rules()
