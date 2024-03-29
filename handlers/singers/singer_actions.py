import datetime
import inspect
from calendar import monthrange, weekday
from random import randint

from config import VIP, VIP2
from loader import bot, log, JOKES
from database_control import db_singer, db_songs, db_event, db_attendance
from telebot.custom_filters import TextFilter
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from misc import dicts, keys, tools
from misc.dictionaries import callback_dictionary as cd


@bot.message_handler(commands=["attendance"])
def display_months_to_send_spam(message: Message):
    """Display buttons of months with upcoming events"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    call_config = cd.upcoming_month_text
    data = []
    current_date = datetime.date.today()
    year = current_date.year
    months = [i-1 for i in range(current_date.month, current_date.month + 3)]

    for month_id in months:
        start_year = year if month_id < 12 else year+1
        start_month = (month_id % 12) + 1
        start_day = 1 if current_date.month != start_month else current_date.day
        time_delta = datetime.timedelta(days=monthrange(start_year, start_month)[1])

        event_list = db_event.search_events_by_date_interval(
            f"{start_year}-{start_month:02}-{start_day:02}",
            f"{datetime.date(start_year, start_month, 1) + time_delta}",
            message.from_user.id
        )

        rehearsals, events, concerts = 0, 0, 0
        for _, event_type, *_ in event_list:
            if event_type == 1:
                events += 1
            elif event_type == 2:
                concerts += 1
            elif event_type == 3:
                rehearsals += 1

        text = f"{start_year} {dicts.events.MONTHS[month_id % 12]}:     {rehearsals} 🔔  {events} 💃  {concerts} 🎪"
        data.append(
            {"text": text, "callback_data": f"{call_config}:{start_year}:{start_month:02}:{start_day:02}"}
        )

    bot.send_message(
        message.chat.id, dicts.events.select_month_text, reply_markup=keys.buttons.buttons_markup(data, row=1, line=6)
    )


@bot.message_handler(commands=["suits"])
def edit_singer_suits(message: Message):
    """Display singer suits and buttons to add or remove"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    singer_id = db_singer.get_singer_id(message.chat.id)
    suits = db_singer.get_all_suits()
    singer_suits = db_singer.get_singer_suits(singer_id)
    suit_names = '\n'.join([f'🥋 {name}' for _, name in singer_suits])

    if not suits:
        msg = dicts.singers.suits_not_available_text
        bot.send_message(message.chat.id, msg)
        return

    if not singer_suits:
        msg = dicts.singers.no_suit_text
        data = [
            {"text": dicts.buttons.add_btn_text, "callback_data": f"{cd.singer_suit_text}:add:{singer_id}"},
            {"text": " ", "callback_data": f"{cd.EMTPY_FIELD}"}
        ]
    elif len(singer_suits) == len(suits):
        msg = f"{dicts.singers.available_suits_text}\n{suit_names}\n\n{dicts.singers.too_many_suits_text}"
        data = [
            {"text": " ", "callback_data": f"{cd.EMTPY_FIELD}"},
            {"text": dicts.buttons.remove_btn_text, "callback_data": f"{cd.singer_suit_text}:remove:{singer_id}"}
        ]
    else:
        msg = f"{dicts.singers.available_suits_text}\n{suit_names}\n\n{dicts.singers.what_to_do_text}"
        data = [
            {"text": dicts.buttons.add_btn_text, "callback_data": f"{cd.singer_suit_text}:add:{singer_id}"},
            {"text": dicts.buttons.remove_btn_text, "callback_data": f"{cd.singer_suit_text}:remove:{singer_id}"}
        ]

    data.append({"text": dicts.buttons.show_all_suits_btn_text, "callback_data": f"{cd.display_suit_photos_text}"})
    bot.send_message(message.chat.id, msg, reply_markup=keys.buttons.buttons_markup(data))

    if db_singer.is_admin(message.chat.id):
        admin_msg = f"{dicts.buttons.admin_buttons_text}"
        data = [{"text": dicts.buttons.more_options_btn_text, "callback_data": f"{cd.display_suit_buttons_text}"}]
        bot.send_message(message.chat.id, admin_msg, reply_markup=keys.buttons.buttons_markup(data))


@bot.message_handler(commands=["songs"])
def chose_song_filter(message: Message):
    """Display buttons for selecting the output of all songs, in work or concert program."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    call_config = cd.song_filter_text
    data = [{"text": dicts.singers.song_name_search_text, "switch_inline_query_current_chat": "a"}]  # inline search
    for filter_id, text in enumerate(dicts.singers.song_filter_text_tuple):
        data.append({"text": text, "callback_data": f"{call_config}:{filter_id}"})

    bot.send_message(
        message.chat.id, dicts.singers.choose_filter_text,
        reply_markup=keys.buttons.buttons_markup(data)
    )


@bot.callback_query_handler(func=None, calendar_config=keys.call.upcoming_month.filter())
def display_event_and_attendance_buttons(call: CallbackQuery):
    """Display list of event and attendance buttons"""

    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t {call.data}\t\t {call.from_user.username} {call.from_user.full_name}")

    _, year, month, day = call.data.split(":")

    call_config_event = cd.event_display_text
    call_config_attendance = cd.mass_edit_attendance_text
    time_delta = datetime.timedelta(days=monthrange(int(year), int(month))[1])
    event_list = db_event.search_events_by_date_interval(
        f"{year}-{month}-{day}",
        f"{datetime.date(int(year), int(month), 1) + time_delta}",
        call.message.chat.id
    )

    data = []

    for event_id, event_type, event_name, event_date, event_time in event_list:
        event_year, event_month, event_day = event_date.split("-")
        week_day_index = weekday(int(event_year), int(event_month), int(event_day))
        event_text = f"{int(event_day)}{dicts.events.WEEK_DAYS[week_day_index]}" \
                     f"{dicts.events.event_type_pics_tuple[int(event_type)]} {event_time}"
        data.append({"text": event_text, "callback_data": f"{call_config_event}:{event_id}"})
        for i, attendance_text in enumerate(dicts.attends.set_attendance_text_tuple):
            data.append({"text": attendance_text, "callback_data": f"{call_config_attendance}:{event_id}:{i}"})

    msg = f"{dicts.events.current_events_text} " \
          f"{dicts.events.MONTHS[int(month) - 1]} {year} года:"
    markup = keys.buttons.buttons_markup(data, row=3)

    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)


@bot.callback_query_handler(func=None, singer_config=keys.call.display_suit_photos_callback.filter())
def show_suit_photos(call: CallbackQuery):
    """Display photos of all suits"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    suits = db_singer.get_all_suits()
    tools.display_suit_photos(call.message, suits)
    bot.delete_message(call.message.chat.id, call.message.id)
    edit_singer_suits(call.message)


@bot.callback_query_handler(func=None, singer_config=keys.call.singer_suit_callback.filter())
def edit_suits_buttons(call: CallbackQuery):
    """Display buttons to add or remove suit"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, option, singer_id = call.data.split(":")

    if option == "add":
        items = db_singer.get_available_suits(singer_id)
    elif option == "remove":
        items = db_singer.get_singer_suits(singer_id)
    else:
        bot.send_message(call.message.chat.id, dicts.changes.ERROR_text)
        bot.delete_message(call.message.chat.id, call.message.id)
        return

    msg, data = tools.generate_items_data_with_option(option, singer_id, items, "suit")
    bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=keys.buttons.buttons_markup(data))


@bot.callback_query_handler(func=None, singer_config=keys.call.song_filter_callback.filter())
def show_songs(call: CallbackQuery):
    """Display buttons with all song names, songs in work or upcoming concerts."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, filter_id = call.data.split(":")
    data = []
    call_config = cd.song_info_text

    if filter_id == "0":
        songs = db_songs.get_all_songs()

    elif filter_id == "1":
        start_date = datetime.datetime.now().date()
        end_date = start_date + datetime.timedelta(days=365)
        songs = db_songs.get_songs_in_work(2, f"{start_date}", f"{end_date}")

    else:
        actual_concerts = db_event.search_future_events_by_event_type(2, datetime.datetime.now().date())
        call_config = cd.concert_filter_text
        if not actual_concerts:
            bot.send_message(call.message.chat.id, dicts.singers.no_concerts_planned)
            return
        for concert_id, concert_name, date, _ in actual_concerts:
            _, month, day = date.split("-")
            text = f"{concert_name} {int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]}"
            data.append({"text": text, "callback_data": f"{call_config}:{concert_id}"})
        msg = dicts.singers.choose_concert_text
        markup = keys.buttons.buttons_markup(data)
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)
        return

    if songs:
        for song_id, text, _ in songs:
            data.append({"text": text, "callback_data": f"{call_config}:{song_id}"})
        msg = dicts.songs.which_song_text
        markup = keys.buttons.buttons_markup(data)
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)
    else:
        bot.edit_message_text(dicts.songs.no_songs_text, call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=None, singer_config=keys.call.concert_filter_callback.filter())
def concert_songs(call: CallbackQuery):
    """Display buttons with song names for a concert program."""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    data = []
    songs = db_songs.get_songs_by_event_id(event_id)
    call_config = cd.song_info_text

    if songs:
        for song_id, text, _ in songs:
            data.append({"text": text, "callback_data": f"{call_config}:{song_id}"})

        msg = dicts.songs.which_song_text
        markup = keys.buttons.buttons_markup(data, event_id=event_id)
        bot.edit_message_text(msg, call.message.chat.id, call.message.id, reply_markup=markup)

    else:
        bot.send_message(call.message.chat.id, dicts.songs.no_songs_text)

    # Admin can change the record about the event
    singer_id = call.from_user.id

    if db_singer.is_admin(singer_id):
        msg = f"{dicts.buttons.admin_buttons_text}\n{dicts.songs.wanna_add_text}"
        bot.send_message(
            call.message.chat.id,
            msg,
            reply_markup=keys.buttons.add_songs_to_concert_buttons(event_id)
        )


@bot.callback_query_handler(func=None, singer_config=keys.call.buttons_roll_callback.filter())
def rolling_callback_buttons(call: CallbackQuery):
    """Roll a page with buttons"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t{call.message.id}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, roll_bar_id, direction, index, event_id = call.data.split(":")
    roll_bar_id = int(roll_bar_id)

    if not keys.buttons.ButtonsKeeper.data_exists(roll_bar_id):
        bot.edit_message_text(dicts.changes.ERROR_text, call.message.chat.id, call.message.id, reply_markup=None)
        return

    btn_keeper = keys.buttons.ButtonsKeeper(roll_bar_id)

    if direction == "previous":
        btn_keeper.i -= 1
    elif direction == "next":
        btn_keeper.i += 1

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.id,
        reply_markup=keys.buttons.buttons_markup(data=btn_keeper.data, roll_bar_id=roll_bar_id,
                                                 multiple=True, row=btn_keeper.row)
    )


@bot.callback_query_handler(func=None, calendar_config=keys.call.show_event_callback.filter())
def show_event(call: CallbackQuery):
    """Display info about the chosen event"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    _, event_id = call.data.split(":")
    _, event_type, event_name, event_date, time, location_id, comment = db_event.search_event_by_id(event_id)
    location_data = db_event.search_location_by_id(location_id)
    telegram_id = call.from_user.id

    _, month, day = event_date.split("-")
    event_date_text = f"{int(day)} {dicts.events.chosen_months_text_tuple[int(month) - 1]}"

    msg = f"{event_name} {event_date_text} в {time}\n"

    if location_data:
        msg += f"{dicts.events.location_text} {location_data[0]}\n"
        bot.send_message(telegram_id, location_data[1], reply_markup=keys.buttons.close_markup)

    if event_type == 2:
        songs = db_songs.get_songs_by_event_id(event_id)
        suit = db_event.get_suit_by_event_id(event_id)

        if suit:
            msg += f"\n{dicts.events.suit_for_event_text}\n{suit[1]}\n"

        msg += f"\n{dicts.events.repertoire_text}\n"
        if songs:
            for _, song, _ in songs:
                msg += f"🎵 {song}\n"
        else:
            msg += f"{dicts.events.repertoire_is_empty_text}\n"

    if comment:
        msg += f"\n{dicts.events.comment_text}\n{comment}\n"

    # ask a singer to set the attendance
    singer_id = db_singer.get_singer_id(telegram_id)

    attendance = db_attendance.get_singer_attendance_for_event(event_id, singer_id)
    if attendance:
        call_config = cd.singer_attendance_text
        data = [
            {"text": text, "callback_data": f"{call_config}:edit:{event_id}:{i}"}
            for i, text in enumerate(dicts.attends.set_attendance_text_tuple)
        ]
        if attendance[0] == 0 or attendance[0] == 1:
            msg += f"\n{dicts.attends.chosen_attendance_text}\n" \
                   f"{dicts.attends.set_attendance_text_tuple[attendance[0]]}\n" \
                   f"\n{dicts.attends.wanna_change_text}"
        else:
            msg += f"\n{dicts.attends.select_attendance_text}"

        markup = keys.buttons.buttons_markup(data)
        bot.send_message(telegram_id, msg, reply_markup=markup)

    elif telegram_id != int(VIP) and telegram_id != int(VIP2):
        msg += f"\n{dicts.attends.you_not_participate_text}"
        bot.send_message(telegram_id, msg, reply_markup=keys.buttons.close_markup)

    else:
        bot.send_message(telegram_id, msg, reply_markup=keys.buttons.close_markup)

    # Admin can change the record about the event
    if db_singer.is_admin(telegram_id):
        item_type = "event"
        markup = keys.buttons.show_participation_button(event_id)

        for buttons in keys.buttons.change_buttons(item_type, event_id).keyboard:
            markup.add(*buttons)

        msg = f"{dicts.buttons.admin_buttons_text}\n{dicts.changes.need_something_text}"
        bot.send_message(telegram_id, msg, reply_markup=markup)


@bot.callback_query_handler(func=None, calendar_config=keys.call.close_button.filter())
def close_btn(call: CallbackQuery):
    """Remove a block of the buttons"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    roll_bar_id = call.data.split(":")[1]
    roll_bar_id = int(roll_bar_id) if roll_bar_id.isdigit() else 0

    if keys.buttons.ButtonsKeeper.data_exists(roll_bar_id):
        keys.buttons.ButtonsKeeper.delete_btn(roll_bar_id)

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(func=lambda c: c.data == "close")
def temporary_close_btn(call: CallbackQuery):   # TODO: Delete after 2022-08-20
    """Remove an old block of the buttons"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{call.data}\t\t"
             f"{call.from_user.username} {call.from_user.full_name}")

    bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.calendar_text_list, ignore_case=True))
def calendar_message(message: Message):
    """Answer to type a command /calendar"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.calendar_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.songs_text_list, ignore_case=True))
def song_message(message: Message):
    """Answer to type a command /songs"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.song_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.suits_text_list, ignore_case=True))
def suit_message(message: Message):
    """Answer to type a command /suits"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.via_bot:
        return
    bot.send_message(message.chat.id, dicts.singers.suit_command_text, reply_to_message_id=message.id)


@bot.message_handler(text=TextFilter(contains=dicts.filters.boring_text_list, ignore_case=True))
def boring_message(message: Message):
    """Send a random joke into the chat"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.via_bot:
        return
    bot.register_next_step_handler(message, joking)
    bot.send_message(message.chat.id, dicts.singers.do_you_wanna_my_joke_text,
                     reply_to_message_id=message.id, reply_markup=keys.buttons.accept_markup)


@bot.message_handler(text=TextFilter(contains=dicts.filters.fool_text_list, ignore_case=True))
def fool_message(message: Message):
    """Answer for the fool"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")

    if message.via_bot:
        return
    msg = randomizer(dicts.jokes.embarrassed_text_tuple)
    bot.send_message(message.chat.id, msg, reply_to_message_id=message.id)


def check_commands(message: Message):
    if (message.text[0] == "/") or message.via_bot:
        return
    return message


@bot.message_handler(func=check_commands)
def nothing_to_say(message: Message):
    """Random answer on unrecognised message"""

    # debug
    func_name = f"{inspect.currentframe()}".split(" ")[-1]
    log.info(f"{__name__} <{func_name}\t{message.text}\t\t"
             f"{message.from_user.username} {message.from_user.full_name}")
    log.info(f"Saved Messages: {keys.buttons.ButtonsKeeper.get_saved_messages()}")

    if JOKES:
        text = eval(randomizer(JOKES))
    else:
        text = dicts.singers.nothing_to_say_text

    bot.forward_message(VIP, message.chat.id, message.id, disable_notification=True)
    bot.send_message(VIP, text, disable_notification=True)
    bot.send_message(message.chat.id, text)


def joking(message: Message):
    msg = randomizer(dicts.jokes.random_jokes_text_tuple)
    bot.send_message(message.chat.id, msg, reply_markup=ReplyKeyboardRemove())


def randomizer(items):
    """Takes items and returns a random item"""
    i = randint(0, len(items) - 1)
    return items[i]
