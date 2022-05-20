from datetime import date
from loader import bot
from telebot.types import CallbackQuery
from keyboards.inline.callback_datas import show_singer_callback, info_callback, edit_voice_callback, \
    attendance_intervals_callback
from keyboards.inline.choice_buttons import singer_info_buttons, callback_buttons
from misc.messages.singer_dictionary import what_to_do_text, singer_not_exists_text
from misc.messages import changes_dictionary as ch_d, attendance_dictionary as at_d
from misc.edit_functions import display_suits, display_voices
from misc.edit_functions import edit_voices
from database_control import db_singer, db_attendance


@bot.callback_query_handler(func=None, singer_config=show_singer_callback.filter())
def display_singer_info(call: CallbackQuery):
    """Display info buttons"""

    singer_id = int(call.data.split(":")[1])
    print(f"display_singer_info {call.data} {db_singer.singer_exists_by_id(singer_id)}")

    if not db_singer.singer_exists_by_id(singer_id):
        sticker_id = "CAACAgIAAxkBAAET3UVielVmblxfxH0PWmMyPceLASLkoQACRAADa-18Cs96SavCm2JLJAQ"
        bot.send_message(call.message.chat.id, singer_not_exists_text)
        bot.send_sticker(call.message.chat.id, sticker_id)
        return

    telegram_name = db_singer.get_singer_telegram_name(singer_id)
    reply_markup = singer_info_buttons(telegram_name, singer_id, ch_d.info_button_names_text_tuple)
    bot.send_message(call.from_user.id, what_to_do_text, reply_markup=reply_markup)


@bot.callback_query_handler(func=None, singer_config=info_callback.filter())
def singer_menu(call: CallbackQuery):
    """Display """

    _, option_id, singer_id = call.data.split(":")
    singer_id = int(singer_id)
    print(f"singer_menu {call.data}")

    if option_id == "0":  # Голос
        display_voices(call.message, singer_id)

    elif option_id == "1":  # Костюмы
        display_suits(call.message, singer_id)

    elif option_id == "2":  # Посещаемость
        call_config = "attendance_intervals"
        data = []
        msg = "Выберите интервал:"

        for i, interval in enumerate(at_d.attendance_interval_text_tuple):
            data.append((interval, f"{call_config}:{i}:{singer_id}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))

    elif option_id == "3":  # Комментарий
        msg = "Нечего комментировать."
        bot.send_message(call.from_user.id, msg)

    elif option_id == "4":  # УДАЛИТЬ
        call_config = "delete_confirmation"
        item_type = "singer"
        item_name = db_singer.get_singer_fullname(singer_id)
        data = []
        msg = f"{ch_d.delete_confirmation_text} {item_name}?"

        for i, answer in enumerate(ch_d.delete_confirmation_text_tuple):
            data.append((answer, f"{call_config}:{item_type}:{singer_id}:{i}"))

        bot.send_message(call.message.chat.id, msg, reply_markup=callback_buttons(data))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=None)

    else:
        print(f"singer_menu again !!! {call.data}")


@bot.callback_query_handler(func=None, singer_config=edit_voice_callback.filter())
def edit_voice_buttons(call: CallbackQuery):
    """Display buttons to add or remove voice"""
    edit_voices(call)


@bot.callback_query_handler(func=None, singer_config=attendance_intervals_callback.filter())
def display_attendance(call: CallbackQuery):
    """Display attendance for a singer"""

    print(f"display_attendance {call.data}")
    _, interval, singer_id = call.data.split(":")
    start_date = db_singer.get_singer_join_date(int(singer_id))
    end_date = date.today()
    msg = at_d.attendance_interval_text_tuple[2]

    if interval == "0":
        msg = at_d.attendance_interval_text_tuple[0]
        month = str(end_date.month - 1).zfill(2)
        day = str(end_date.day).zfill(2)
        new_date = f"{end_date.year}-{month}-{day}"
        if start_date < new_date:
            start_date = new_date

    elif interval == "1":
        msg = at_d.attendance_interval_text_tuple[0]
        month = str(end_date.month).zfill(2)
        day = str(end_date.day).zfill(2)
        new_date = f"{end_date.year - 1}-{month}-{day}"
        if start_date < new_date:
            start_date = new_date

    attendance = db_attendance.get_attendance_by_interval(int(singer_id), start_date,
                                                          end_date.strftime('%Y-%m-%d'))
    print(f"{attendance}")

    if not attendance:
        bot.send_message(call.message.chat.id, at_d.no_attendance_text)

    msg += f"\n{at_d.attendance_description_text_tuple[0]}: {attendance.count('0')}" \
           f"\n{at_d.attendance_description_text_tuple[1]}: {attendance.count('1')}" \
           f"\n{at_d.attendance_description_text_tuple[2]}: {attendance.count('2')}"

    bot.send_message(call.message.chat.id, msg)
