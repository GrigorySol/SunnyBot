from datetime import date

from config import VIP
from loader import bot
from telebot.types import CallbackQuery, Message
from misc.edit_functions import display_suits, display_voices, edit_voices
from database_control import db_singer, db_attendance
from misc import dicts, keys


@bot.callback_query_handler(func=None, singer_config=keys.call.show_singer_callback.filter())
def display_singer_info(call: CallbackQuery):
    """Display info buttons"""

    singer_id = int(call.data.split(":")[1])
    print(f"display_singer_info {call.data} {db_singer.singer_exists_by_id(singer_id)}")

    if not db_singer.singer_exists_by_id(singer_id):
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.from_user.id, dicts.singers.singer_not_exists_text)
        bot.send_sticker(call.from_user.id, sticker_id)
        return

    comment = db_singer.get_singer_comment(singer_id)
    msg = dicts.singers.what_to_do_text
    if comment:
        msg = f"{dicts.singers.singer_comment_text}\n{comment}\n\n{msg}"

    telegram_name = db_singer.get_singer_telegram_name(singer_id)
    markup = keys.buttons.singer_info_buttons(telegram_name, singer_id, dicts.changes.edit_singer_text_tuple)
    bot.send_message(call.from_user.id, msg, reply_markup=markup)

    if call.message:
        bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.info_callback.filter())
def singer_menu(call: CallbackQuery):
    """Edit singer's info or DELETE a singer"""

    _, option_id, singer_id = call.data.split(":")
    print(f"singer_menu {call.data}")

    if option_id == "0":  # Голос
        display_voices(call.message, singer_id)

    elif option_id == "1":  # Костюмы
        display_suits(call.message, singer_id)

    elif option_id == "2":  # Посещаемость
        call_config = "attendance_intervals"
        data = []
        msg = dicts.attends.choose_interval_text

        for i, interval in enumerate(dicts.attends.attendance_interval_text_tuple):
            data.append((interval, f"{call_config}:{i}:{singer_id}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.callback_buttons(data))

    elif option_id == "3":  # Комментарий
        msg = bot.send_message(call.message.chat.id, dicts.changes.enter_new_comment_text)
        bot.register_next_step_handler(msg, enter_new_singer_comment, singer_id)

    elif option_id == "4":  # Имя/Фамилию
        text = f"{dicts.changes.first_last_name_text} " \
               f"{db_singer.get_singer_fullname(singer_id)} " \
               f"{dicts.changes.would_be_changed_text}\n" \
               f"{dicts.changes.enter_new_name_text}"
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, enter_new_singer_name, singer_id)

    elif option_id == "5":  # УДАЛИТЬ
        call_config = "delete_confirmation"
        item_type = "singer"
        item_name = db_singer.get_singer_fullname(singer_id)
        data = []
        msg = f"{dicts.changes.delete_confirmation_text} {item_name}?"

        for i, answer in enumerate(dicts.changes.delete_confirmation_text_tuple):
            data.append((answer, f"{call_config}:{item_type}:{singer_id}:{i}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=keys.buttons.callback_buttons(data))

    bot.delete_message(call.message.chat.id, call.message.id)


def enter_new_singer_name(message: Message, singer_id):
    """Update the first and last name for a singer"""

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if " " in message.text and message.text.count(" ") < 2:
        first_name, last_name = message.text.split(" ")
    else:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if db_singer.edit_singer_name(singer_id, first_name, last_name):
        bot.send_message(message.chat.id, dicts.changes.singer_name_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_singer_name, singer_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {singer_id} "
        bot.send_message(VIP, vip_msg)


def enter_new_singer_comment(message: Message, singer_id):
    """Update the comment for a singer"""

    if not message.text or "/" in message.text:
        bot.send_message(message.chat.id, dicts.singers.CANCELED)
        return

    if db_singer.edit_singer_comment(singer_id, message.text):
        bot.send_message(message.chat.id, dicts.changes.comment_changed_text)

    else:
        msg = bot.send_message(message.chat.id, dicts.changes.ERROR_text)
        bot.register_next_step_handler(msg, enter_new_singer_comment, singer_id)
        vip_msg = f"ERROR in enter_new_event_name\nData: {message.text} {singer_id} "
        bot.send_message(VIP, vip_msg)


@bot.callback_query_handler(func=None, singer_config=keys.call.edit_voice_callback.filter())
def edit_voice_buttons(call: CallbackQuery):
    """Display buttons to add or remove voice"""
    edit_voices(call)
    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.attendance_intervals_callback.filter())
def display_attendance(call: CallbackQuery):
    """Display attendance for a singer"""

    print(f"display_attendance {call.data}")
    _, interval, singer_id = call.data.split(":")
    start_date = db_singer.get_singer_join_date(int(singer_id))
    end_date = date.today()
    msg = dicts.attends.attendance_interval_text_tuple[2]

    if interval == "0":
        msg = dicts.attends.attendance_interval_text_tuple[0]
        month = str(end_date.month - 1).zfill(2)
        day = str(end_date.day).zfill(2)
        new_date = f"{end_date.year}-{month}-{day}"
        if start_date < new_date:
            start_date = new_date

    elif interval == "1":
        msg = dicts.attends.attendance_interval_text_tuple[0]
        month = str(end_date.month).zfill(2)
        day = str(end_date.day).zfill(2)
        new_date = f"{end_date.year - 1}-{month}-{day}"
        if start_date < new_date:
            start_date = new_date

    attendance = db_attendance.get_attendance_by_interval(int(singer_id), start_date,
                                                          end_date.strftime('%Y-%m-%d'))
    print(f"{attendance}")

    if not attendance:
        bot.send_message(call.message.chat.id, dicts.attends.no_attendance_text)
        return

    msg += f"\n{dicts.attends.attendance_description_text_tuple[0]}: {attendance.count('0')}" \
           f"\n{dicts.attends.attendance_description_text_tuple[1]}: {attendance.count('1')}" \
           f"\n{dicts.attends.attendance_description_text_tuple[2]}: {attendance.count('2')}"

    bot.send_message(call.message.chat.id, msg)
    bot.delete_message(call.message.chat.id, call.message.id)
