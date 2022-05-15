import sqlite3


def get_attendance_by_event_id(event_id):
    """Return all (singer fullname, telegram_name, attend) and attend from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.first_name || ' ' || singers.last_name "
                       "AS fullname, singers.telegram_name, attendance.attend "
                       "FROM attendance "
                       "JOIN singers ON singers.id = attendance.singer_id "
                       "WHERE event_id = ? ORDER BY attend", (event_id,))
        return cursor.fetchall()


def get_attendance_by_singer_id(singer_id):
    """Return all (event id, attend) from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT event_id, attend FROM attendance WHERE singer_id = ?", (singer_id,))
        return cursor.fetchall()


def get_attendance_interval_by_singer(singer_id, start_date, end_date):
    """Return (event_id, attend) using singer_id and date interval from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT attendance.event_id, attendance.attend FROM attendance "
                       "JOIN events ON events.id = attendance.event_id "
                       "WHERE attendance.singer_id = ? AND events.date BETWEEN ? AND ?",
                       (singer_id, start_date, end_date))
        return cursor.fetchall()


def get_all_telegram_singer_id_by_event_id(event_id):
    """Return all telegram singer_id's from the database."""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("SELECT singers.singer_id FROM singers "
                       "JOIN attendance ON attendance.singer_id = singers.id "
                       "WHERE attendance.event_id = ?", (event_id,))
        return cursor.fetchall()


# INSERT

def create_new_attendance(event_id):
    """Add all singers and event to the attendance table in the database. TODO: Add singers"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        return


# UPDATE

def edit_singer_attendance(event_id, singer_id, attend):
    """Edit singer attendance for an event in the database"""
    with sqlite3.connect("database_control/sunny_bot.db") as db:
        cursor = db.cursor()

        # language=SQLITE-SQL
        cursor.execute("UPDATE attendance SET attend = ? "
                       "WHERE event_id = ? AND singer_id = ?", (event_id, singer_id, attend))


# DELETE

