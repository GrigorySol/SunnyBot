"""
Fork from the pyTelegramBotAPI github example repo
"""

import calendar
from datetime import date, timedelta

from keyboards.inline.callback_datas import calendar_factory, calendar_zoom
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from misc.messages.event_dictionary import next_button_text, prev_button_text, zoom_out_text

EMTPY_FIELD = 'calendar_button'
WEEK_DAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")
MONTHS = ((1, "Январь"), (2, "Февраль"), (3, "Март"), (4, "Апрель"), (5, "Май"), (6, "Июнь"),
          (7, "Июль"), (8, "Август"), (9, "Сентябрь"), (10, "Октябрь"), (11, "Ноябрь"), (12, "Декабрь"))

CLOSE_BTN = InlineKeyboardButton("Закрыть", callback_data="close")


def generate_calendar_days(year: int, month: int, event_id=0):
    """
    Generates buttons grid with month + year, weeks, days,
    next, previous, zoom out and close buttons
    """

    keyboard = InlineKeyboardMarkup(row_width=7)
    today = date.today()
    text_month = ""

    for i, m in MONTHS:
        if i == month:
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
            if day == today.day and today.year == year and today.month == month:
                day_name = '☀️'
            elif day != 0:
                day_name = str(day)
            week_buttons.append(
                InlineKeyboardButton(
                    text=day_name,
                    callback_data=f"calendar_data:{event_id}:{year}:{month}:{day}"
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
            callback_data=calendar_factory.new(event_id=event_id, year=year, month=month_number)
        )
        for month_number, month in MONTHS
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
