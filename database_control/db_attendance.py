import sqlite3
from config import BOT_DB


def get_attendance_by_event_id(event_id):
    """Return all (singer id, fullname, telegram_name, attend) from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name, attendance.attend "
                       "FROM attendance "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE event_id = ? ORDER BY attend", (event_id,))
        return cursor.fetchall()


def get_not_participating_by_event_id(event_id):
    """Return all (singer id, fullname, telegram_name) who do not participate in an event from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name "
                       "FROM singers EXCEPT "
                       "SELECT singers.id, singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name "
                       "FROM attendance "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE event_id = ? ORDER BY fullname", (event_id,))
        return cursor.fetchall()


def get_attendance_by_interval(singer_id, start_date, end_date):
    """Return (attend) using singer_id and date interval from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT GROUP_CONCAT(attendance.attend, '') FROM attendance "
                       "JOIN events ON events.id = attendance.event_id "
                       "WHERE attendance.singer_id = ? AND events.date BETWEEN ? AND ?",
                       (singer_id, start_date, end_date))
        return cursor.fetchone()[0]


def get_singer_attendance_for_event(event_id, singer_id):
    """Return str 0, 1 or 2 if attendance record exists in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("SELECT attend FROM attendance WHERE event_id = ? AND singer_id = ?", (event_id, singer_id))
        return cursor.fetchone()


def get_all_telegram_singer_id_by_event_id(event_id):
    """Return all telegram singer_id's from the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.telegram_id FROM singers "
                       "JOIN attendance ON attendance.singer_id = singers.id "
                       "WHERE attendance.event_id = ? ORDER BY singers.first_name", (event_id,))
        return cursor.fetchall()


# INSERT

def add_all_singers_attendance(event_id: int):
    """Add an event and singers with voices to the attendance table in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO attendance (event_id, singer_id) "
                       "SELECT DISTINCT ?, singer_id FROM singer_voice "
                       "EXCEPT SELECT event_id, singer_id FROM attendance", (event_id,))


def add_singer_attendance(event_id, singer_id):
    """Add singers  with voices and an event to the attendance table in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO attendance (event_id, singer_id) VALUES (?, ?)", (event_id, singer_id))


def magic_attendance(date):
    """Add singers with voices for all events to the attendance table in the database."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("INSERT INTO attendance (event_id, singer_id) "
                       "SELECT DISTINCT events.id, singer_voice.singer_id FROM events, singer_voice "
                       "WHERE events.date > date(?) "
                       "EXCEPT SELECT event_id, singer_id FROM attendance", (date,))


# UPDATE

def edit_singer_attendance(event_id, telegram_id, attend):
    """Edit singer attendance for an event in the database/"""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("UPDATE attendance SET attend = ? "
                       "WHERE attendance.event_id = ? AND attendance.singer_id = "
                       "(SELECT id FROM singers WHERE telegram_id = ?)", (attend, event_id, telegram_id))


# DELETE

def remove_all_singers_attendance(event_id):
    """Remove all singers from an event."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM attendance WHERE event_id = ?", (event_id,))


def remove_singer_attendance(event_id, singer_id):
    """Remove singer attendance check from an event."""
    with sqlite3.connect(BOT_DB) as db:
        cursor = db.cursor()

        cursor.execute("DELETE FROM attendance WHERE event_id = ? AND singer_id = ?", (event_id, singer_id))
