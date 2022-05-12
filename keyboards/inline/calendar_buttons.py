"""
Fork from the pyTelegramBotAPI github example repo
"""

import calendar
from datetime import date, timedelta

from database_control.db_event import search_event_by_date
from keyboards.inline.callback_datas import calendar_factory, calendar_zoom
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from misc.messages.event_dictionary import next_button_text, prev_button_text, zoom_out_text, WEEK_DAYS, MONTHS

EMTPY_FIELD = 'calendar_button'

CLOSE_BTN = InlineKeyboardButton("Закрыть", callback_data="close")


def generate_calendar_days(year: int, month: int, event_id=0, _id=None):
    """
    Generates buttons grid with month + year, weeks, days,
    next, previous, zoom out and close buttons
    """

    keyboard = InlineKeyboardMarkup(row_width=7)

    # event_datetime = get_all_events_datetime()
    # event_days = []
    # for day_time in event_datetime:
    #     day = day_time[0].split(" ")[0]
    #     if day not in event_days:
    #         event_days.append(day)

    today = date.today()
    text_month = ""

    for i, m in enumerate(MONTHS):
        if (i+1) == month:
            text_month = m
            break

    # Create TOP button with month and year
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=month, day=1).strftime(f"{text_month} %Y"),
            callback_data=EMTPY_FIELD
        )
    )
    # Create WEEK DAYS buttons
    keyboard.add(*[
        InlineKeyboardButton(
            text=day,
            callback_data=EMTPY_FIELD
        )
        for day in WEEK_DAYS
    ])

    # Create DAYS buttons
    for week in calendar.Calendar().monthdayscalendar(year=year, month=month):
        week_buttons = []
        for day in week:
            day_name = ' '
            current_day = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
            event = search_event_by_date(f"{current_day}%")
            if current_day == str(today):
                day_name = '☀️'
            elif day and event:
                if event[-1][1] == 1:
                    day_name = '💃'
                elif event[-1][1] == 2:
                    day_name = '🎪'      # 🏛 🪗 👨‍🦽  📝
                else:
                    day_name = '🔔'
            elif day:
                day_name = str(day)
            week_buttons.append(
                InlineKeyboardButton(
                    text=day_name,
                    callback_data=f"calendar_data:{event_id}:{year}:{month}:{day}:{_id}"
                )
            )
        keyboard.add(*week_buttons)

    # Create previous, next, zoom out and close buttons
    previous_date = date(year=year, month=month, day=1) - timedelta(days=1)
    next_date = date(year=year, month=month, day=1) + timedelta(days=31)

    keyboard.add(
        InlineKeyboardButton(
            text=prev_button_text,
            callback_data=calendar_factory.new(event_id=event_id, year=previous_date.year, month=previous_date.month)
        ),
        InlineKeyboardButton(
            text=zoom_out_text,
            callback_data=calendar_zoom.new(event_id=event_id, year=year)
        ),
        InlineKeyboardButton(
            text=next_button_text,
            callback_data=calendar_factory.new(event_id=event_id, year=next_date.year, month=next_date.month)
        ),
    )
    keyboard.add(CLOSE_BTN)

    return keyboard


def generate_calendar_months(year: int, event_id=0):
    """
    Generates buttons grid with year, months,
    next/previous and close buttons
    """

    # Create TOP button with year
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=1, day=1).strftime('Год %Y'),
            callback_data=EMTPY_FIELD
        )
    )

    # Create months buttons
    keyboard.add(*[
        InlineKeyboardButton(
            text=month,
            callback_data=calendar_factory.new(event_id=event_id, year=year, month=month_number+1)
        )
        for month_number, month in enumerate(MONTHS)
    ])

    # Create previous, next and close buttons
    keyboard.add(
        InlineKeyboardButton(
            text=prev_button_text,
            callback_data=calendar_zoom.new(event_id=event_id, year=year - 1)
        ),
        InlineKeyboardButton(
            text=next_button_text,
            callback_data=calendar_zoom.new(event_id=event_id, year=year + 1)
        )
    )
    keyboard.add(CLOSE_BTN)

    return keyboard
