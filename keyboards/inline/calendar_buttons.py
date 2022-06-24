"""
Fork from the pyTelegramBotAPI GitHub example repo
"""

import calendar
from datetime import date, timedelta

from database_control import db_singer
from database_control.db_event import search_event_by_date, search_event_by_date_and_telegram_id
from keyboards.inline.callback_datas import calendar_factory, calendar_zoom
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from misc.messages.event_dictionary import next_button_text, prev_button_text, zoom_out_text, WEEK_DAYS, MONTHS
from misc import callback_dict as cd

EMTPY_FIELD = 'calendar_button'

CLOSE_BTN = InlineKeyboardButton("Закрыть", callback_data=cd.close_text)


def generate_calendar_days(telegram_id: int, year: int, month: int, event_type=0, event_id=0):
    """
    Generates buttons grid with month + year, weeks, days,
    next, previous, zoom out and close buttons
    """

    keyboard = InlineKeyboardMarkup(row_width=7)

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
            if not db_singer.is_admin(telegram_id):
                event = search_event_by_date_and_telegram_id(f"{current_day}%", telegram_id)
            else:
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
                    callback_data=f"{cd.calendar_data_text}:{event_type}:{event_id}:{year}:{month}:{day}"
                )
            )
        keyboard.add(*week_buttons)

    # Create previous, next, zoom out and close buttons
    previous_date = date(year=year, month=month, day=1) - timedelta(days=1)
    next_date = date(year=year, month=month, day=1) + timedelta(days=31)

    keyboard.add(
        InlineKeyboardButton(
            text=prev_button_text,
            callback_data=calendar_factory.new(
                event_type=event_type,
                event_id=event_id,
                year=previous_date.year,
                month=previous_date.month
            )
        ),
        InlineKeyboardButton(
            text=zoom_out_text,
            callback_data=calendar_zoom.new(
                event_type=event_type, event_id=event_id, year=year
            )
        ),
        InlineKeyboardButton(
            text=next_button_text,
            callback_data=calendar_factory.new(
                event_type=event_type,
                event_id=event_id,
                year=next_date.year,
                month=next_date.month
            )
        ),
    )
    keyboard.add(CLOSE_BTN)

    return keyboard


def generate_calendar_months(year: int, event_type=0, event_id=0):
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
            callback_data=calendar_factory.new(
                event_type=event_type,
                event_id=event_id,
                year=year,
                month=month_number + 1
            )
        )
        for month_number, month in enumerate(MONTHS)
    ])

    # Create previous, next and close buttons
    keyboard.add(
        InlineKeyboardButton(
            text=prev_button_text,
            callback_data=calendar_zoom.new(
                event_type=event_type, event_id=event_id, year=year - 1
            )
        ),
        InlineKeyboardButton(
            text=next_button_text,
            callback_data=calendar_zoom.new(
                event_type=event_type, event_id=event_id, year=year + 1
            )
        )
    )
    keyboard.add(CLOSE_BTN)

    return keyboard
